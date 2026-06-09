from __future__ import annotations

import pandas as pd
import pytest
from plotly.graph_objects import Figure

from asaf.isotherm import Isotherm


def test_isotherm_requires_dataframe_with_uptake() -> None:
    with pytest.raises(ValueError, match="data must be provided"):
        Isotherm()

    with pytest.raises(ValueError, match="uptake"):
        Isotherm(pd.DataFrame({"fugacity": [1.0, 2.0]}))


def test_plot_uses_available_fugacity_without_optional_relative_columns() -> None:
    iso = Isotherm(pd.DataFrame({"fugacity": [1.0, 2.0], "uptake": [3.0, 4.0]}))

    fig = iso.plot(fig=Figure())

    assert len(fig.data) == 1
    assert list(fig.data[0].x) == [1.0, 2.0]
    assert fig.layout.xaxis.title.text == "Fugacity (Pa)"


def test_plot_returns_figure_without_showing_by_default(monkeypatch) -> None:
    iso = Isotherm(pd.DataFrame({"fugacity": [1.0, 2.0], "uptake": [3.0, 4.0]}))
    shown = False

    def fake_show(self) -> None:
        nonlocal shown
        shown = True

    monkeypatch.setattr(Figure, "show", fake_show)

    fig = iso.plot()

    assert isinstance(fig, Figure)
    assert shown is False


def test_plot_can_show_explicitly(monkeypatch) -> None:
    iso = Isotherm(pd.DataFrame({"fugacity": [1.0, 2.0], "uptake": [3.0, 4.0]}))
    shown = False

    def fake_show(self) -> None:
        nonlocal shown
        shown = True

    monkeypatch.setattr(Figure, "show", fake_show)

    iso.plot(show=True)

    assert shown is True


def test_plot_auto_uses_pressure_when_fugacity_is_missing() -> None:
    iso = Isotherm(
        pd.DataFrame({"pressure": [10.0, 20.0], "uptake": [3.0, 4.0]}),
        saturation_pressure=100.0,
    )

    fig = iso.plot(fig=Figure())

    assert list(fig.data[0].x) == [10.0, 20.0]
    assert fig.layout.xaxis.title.text == "Pressure (Pa)"
    assert list(iso.dataframe["p/p0"]) == [0.1, 0.2]


def test_saturation_fugacity_and_pressure_create_correct_relative_columns() -> None:
    iso = Isotherm(
        pd.DataFrame(
            {
                "pressure": [10.0, 20.0],
                "fugacity": [8.0, 16.0],
                "uptake": [3.0, 4.0],
            }
        ),
        saturation_fugacity=40.0,
        saturation_pressure=100.0,
    )

    assert list(iso.dataframe["f/f0"]) == [0.2, 0.4]
    assert list(iso.dataframe["p/p0"]) == [0.1, 0.2]


def test_saturation_fugacity_does_not_create_relative_pressure() -> None:
    iso = Isotherm(
        pd.DataFrame({"pressure": [10.0, 20.0], "uptake": [3.0, 4.0]}),
        saturation_fugacity=100.0,
    )

    assert "f/f0" not in iso.dataframe.columns
    assert "p/p0" not in iso.dataframe.columns


def test_plot_metastable_traces_share_group_color_and_use_distinct_dashes() -> None:
    fig = Figure()
    first = Isotherm(
        pd.DataFrame(
            {
                "fugacity": [1.0, 2.0],
                "uptake": [3.0, 4.0],
                "metastable_gas": [2.0, 2.5],
                "metastable_liq": [5.0, 5.5],
            }
        )
    )
    second = Isotherm(pd.DataFrame({"fugacity": [1.0, 2.0], "uptake": [6.0, 7.0]}))

    first.plot(label="first", fig=fig)
    second.plot(label="second", fig=fig)

    assert len(fig.data) == 4
    assert fig.data[0].line.color == fig.data[1].line.color
    assert fig.data[0].line.color == fig.data[2].line.color
    assert fig.data[3].line.color != fig.data[0].line.color
    assert fig.data[1].line.dash == "dash"
    assert fig.data[2].line.dash == "dot"
    assert fig.data[1].showlegend is False
    assert fig.data[2].showlegend is False
    assert fig.data[0].legendgroup == fig.data[1].legendgroup
    assert fig.data[0].legendgroup == fig.data[2].legendgroup


def test_plot_unit_conversion_does_not_mutate_isotherm_data() -> None:
    df = pd.DataFrame(
        {
            "fugacity": [1.0, 2.0],
            "uptake": [3.0, 4.0],
            "metastable_gas": [2.0, 2.5],
        }
    )
    iso = Isotherm(
        df.copy(),
        metadata={"conversion_factors": {"molecules/unitcell->mol/kg": 10.0}},
    )

    fig = iso.plot(fig=Figure(), y_axis="mol/kg")

    assert list(fig.data[0].y) == [30.0, 40.0]
    assert list(fig.data[1].y) == [20.0, 25.0]
    pd.testing.assert_frame_equal(iso.dataframe, df)
    assert iso.uptake_unit == "molecules/unitcell"


def test_plot_defaults_to_current_uptake_unit_after_explicit_conversion() -> None:
    iso = Isotherm(
        pd.DataFrame(
            {
                "fugacity": [1.0, 2.0],
                "uptake": [3.0, 4.0],
                "metastable_gas": [2.0, 2.5],
            }
        )
    )

    iso.set_uptake_unit("g/g", conversion_factor=0.01)
    fig = iso.plot(fig=Figure())

    assert list(fig.data[0].y) == [0.03, 0.04]
    assert list(fig.data[1].y) == [0.02, 0.025]
    assert fig.layout.yaxis.title.text == "Uptake (g/g)"


def test_to_aif_uses_available_columns_without_mutating_dataframe(tmp_path) -> None:
    df = pd.DataFrame({"fugacity": [1.0, 2.0], "uptake": [3.0, 4.0]})
    iso = Isotherm(df.copy(), saturation_fugacity=10.0)

    iso.to_aif(str(tmp_path / "isotherm"))

    assert (tmp_path / "isotherm.aif").exists()
    assert "saturation_fugacity" not in iso.dataframe.columns
    assert "f/f0" in iso.dataframe.columns
