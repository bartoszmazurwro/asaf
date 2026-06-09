"""Provides the Isotherm class to store, manipulate, plot and save adsorption isotherm data."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    from numpy.typing import ArrayLike
    from plotly.graph_objects import Figure

from .utils import quote


class Isotherm:
    """Isotherm class to store, recalculate and save the adsorption isotherm."""

    def __init__(
        self,
        data: pd.DataFrame | None = None,
        saturation_fugacity: float | None = None,
        saturation_pressure: float | None = None,
        metadata: dict[str, Any] | None = None,
        fugacity_unit: str = "Pa",
        uptake_unit: str = "molecules/unitcell",
    ) -> None:
        """Initialize the Isotherm object.

        Parameters
        ----------
        data
            A pandas DataFrame containing the adsorption data. Should contain 'pressure' and 'uptake' columns.
        saturation_fugacity
            The saturation fugacity at given conditions. Used to calculate relative fugacity (f/f0).
        saturation_pressure
            The saturation pressure at given conditions. Used to calculate relative pressure (p/p0).
        metadata
            A dictionary with the simulation metadata.
        uptake_unit
            Units at which uptake is stored. Default value is 'molecules/unitcell'.
        """
        self.dataframe = data
        self._metadata = {}
        self.metadata = metadata
        self._pressure_unit = fugacity_unit
        self._uptake_unit = uptake_unit
        self.saturation_fugacity = saturation_fugacity
        self.saturation_pressure = saturation_pressure

    @property
    def dataframe(self) -> pd.DataFrame:
        """Return dataframe with isotherm data."""
        return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe: pd.DataFrame | None) -> None:
        if dataframe is None:
            raise ValueError("Isotherm data must be provided as a pandas DataFrame.")
        if "uptake" not in dataframe.columns:
            raise ValueError("Isotherm data must contain an 'uptake' column.")
        self._dataframe = dataframe

    @property
    def pressure(self) -> pd.Series | None:
        """Return the pressure column."""
        if "pressure" in self._dataframe.columns:
            return self._dataframe["pressure"]
        else:
            return None

    @pressure.setter
    def pressure(self, pressure: ArrayLike) -> None:
        self._dataframe["pressure"] = pressure

    @property
    def fugacity(self) -> pd.Series | None:
        """Return the fugacity column."""
        if "fugacity" in self._dataframe.columns:
            return self._dataframe["fugacity"]
        else:
            return None

    @property
    def saturation_fugacity(self) -> float | None:
        """Return the saturation fugacity."""
        return self._saturation_fugacity

    @saturation_fugacity.setter
    def saturation_fugacity(self, saturation_fugacity: float | None) -> None:
        if saturation_fugacity is not None and saturation_fugacity <= 0:
            raise ValueError("`saturation_fugacity` must be positive.")
        self._saturation_fugacity = saturation_fugacity
        if saturation_fugacity is not None and self.fugacity is not None:
            self._dataframe["f/f0"] = self.fugacity / saturation_fugacity

    @property
    def saturation_pressure(self) -> float | None:
        """Return the saturation pressure."""
        return self._saturation_pressure

    @saturation_pressure.setter
    def saturation_pressure(self, saturation_pressure: float | None) -> None:
        if saturation_pressure is not None and saturation_pressure <= 0:
            raise ValueError("`saturation_pressure` must be positive.")
        self._saturation_pressure = saturation_pressure
        if saturation_pressure is not None and self.pressure is not None:
            self._dataframe["p/p0"] = self.pressure / saturation_pressure

    @property
    def amount_adsorbed(self) -> pd.Series:
        """Return the uptake column."""
        return self.dataframe["uptake"]

    @property
    def metastable_gas(self) -> pd.Series | None:
        """Return the metastable gas column, if it exists."""
        if "metastable_gas" in self._dataframe.columns:
            return self._dataframe["metastable_gas"]
        else:
            return None

    @property
    def metastable_liq(self) -> pd.Series | None:
        """Return the metastable liquid column, if it exists."""
        if "metastable_liq" in self._dataframe.columns:
            return self._dataframe["metastable_liq"]
        else:
            return None

    @property
    def pressure_unit(self) -> str:
        """Return the current pressure unit."""
        return self._pressure_unit

    def set_pressure_unit(self, target_unit: str, conversion_factor: float) -> None:
        """Convert the pressure column to the target unit using the provided conversion factor."""
        if self.pressure is None:
            raise ValueError(
                "Cannot convert pressure units: no 'pressure' column found."
            )
        self.pressure = self.pressure * conversion_factor
        self._pressure_unit = target_unit

    @property
    def uptake_unit(self) -> str:
        """Return the current uptake unit."""
        return self._uptake_unit

    def set_uptake_unit(
        self, target_unit: str, conversion_factor: float | None = None
    ) -> None:
        """Convert the uptake column to the target unit."""
        conversion_factor = self._uptake_conversion_factor(
            target_unit, conversion_factor
        )

        self.dataframe["uptake"] = self.dataframe["uptake"] * conversion_factor
        if self.metastable_gas is not None:
            self.dataframe["metastable_gas"] = (
                self.dataframe["metastable_gas"] * conversion_factor
            )
        if self.metastable_liq is not None:
            self.dataframe["metastable_liq"] = (
                self.dataframe["metastable_liq"] * conversion_factor
            )

        self._uptake_unit = target_unit

    def _uptake_conversion_factor(
        self, target_unit: str, conversion_factor: float | None = None
    ) -> float:
        """Return the uptake conversion factor from the current unit to target unit."""
        if target_unit == self.uptake_unit:
            return 1.0
        if conversion_factor is not None:
            return conversion_factor

        conv_factors = self.metadata.get("conversion_factors", {})
        current_unit = self.uptake_unit
        forward_key = f"{current_unit}->{target_unit}"
        reverse_key = f"{target_unit}->{current_unit}"

        if forward_key in conv_factors:
            return conv_factors[forward_key]
        if reverse_key in conv_factors:
            return 1 / conv_factors[reverse_key]

        base_unit = "molecules/unitcell"
        key_a = f"{base_unit}->{current_unit}"
        key_b = f"{base_unit}->{target_unit}"
        if key_a in conv_factors and key_b in conv_factors:
            return conv_factors[key_b] / conv_factors[key_a]

        legacy_current = current_unit.replace("/", "_").replace(" ", "_")
        legacy_target = target_unit.replace("/", "_").replace(" ", "_")
        legacy_base = base_unit.replace("/", "_")
        legacy_key_a = f"{legacy_base}__{legacy_current}"
        legacy_key_b = f"{legacy_base}__{legacy_target}"
        if legacy_current == legacy_base and legacy_key_b in conv_factors:
            return conv_factors[legacy_key_b]
        if legacy_target == legacy_base and legacy_key_a in conv_factors:
            return 1 / conv_factors[legacy_key_a]
        if legacy_key_a in conv_factors and legacy_key_b in conv_factors:
            return conv_factors[legacy_key_b] / conv_factors[legacy_key_a]

        raise ValueError(
            f"Conversion factor for {forward_key} was not provided and was not found in metadata."
        )

    @property
    def metadata(self) -> dict[str, Any]:
        """Return the metadata dictionary."""
        return self._metadata

    @metadata.setter
    def metadata(self, metadata: dict[str, Any] | None) -> None:
        if metadata:
            for k, v in metadata.items():
                self._metadata[k] = v

    @staticmethod
    def _axis_definitions() -> dict[str, tuple[tuple[str, ...], str]]:
        """Return supported x-axis aliases, candidate dataframe columns and titles."""
        return {
            "pressure": (("pressure",), "Pressure ({unit})"),
            "fugacity": (("fugacity",), "Fugacity ({unit})"),
            "relative_pressure": (
                ("p/p0", "relative_pressure", "relative pressure"),
                "p/p0",
            ),
            "p/p0": (("p/p0", "relative_pressure", "relative pressure"), "p/p0"),
            "relative_fugacity": (
                ("f/f0", "relative_fugacity", "relative fugacity"),
                "f/f0",
            ),
            "f/f0": (("f/f0", "relative_fugacity", "relative fugacity"), "f/f0"),
            "relative_humidity": (
                ("relative_humidity", "relative humidity", "RH", "rh"),
                "Relative humidity",
            ),
            "humidity": (
                ("relative_humidity", "relative humidity", "RH", "rh"),
                "Relative humidity",
            ),
            "rh": (
                ("relative_humidity", "relative humidity", "RH", "rh"),
                "Relative humidity",
            ),
        }

    def _resolve_x_axis(self, x_axis: str) -> tuple[pd.Series, str]:
        """Resolve a requested x-axis to an existing dataframe column and axis title."""
        axis_definitions = self._axis_definitions()
        auto_priority = (
            "fugacity",
            "pressure",
            "relative_fugacity",
            "relative_pressure",
            "relative_humidity",
        )

        if x_axis == "auto":
            for axis_name in auto_priority:
                columns, title = axis_definitions[axis_name]
                for column in columns:
                    if column in self.dataframe.columns:
                        return self.dataframe[column], title.format(
                            unit=self.pressure_unit
                        )
            valid_columns = "', '".join(
                sorted(
                    {
                        column
                        for columns, _ in axis_definitions.values()
                        for column in columns
                    }
                )
            )
            raise ValueError(
                f"Isotherm data must contain at least one pressure-related column: '{valid_columns}'."
            )

        if x_axis not in axis_definitions:
            valid = "', '".join(["auto", *axis_definitions])
            raise ValueError(f"x_axis must be one of '{valid}'. Got {x_axis!r}.")

        columns, title = axis_definitions[x_axis]
        for column in columns:
            if column in self.dataframe.columns:
                return self.dataframe[column], title.format(unit=self.pressure_unit)

        available = "', '".join(self.dataframe.columns)
        expected = "', '".join(columns)
        raise ValueError(
            f"x_axis={x_axis!r} requires one of '{expected}', but dataframe columns are '{available}'."
        )

    def plot(
        self,
        label: str | None = None,
        fig: Figure | None = None,
        x_axis: str = "auto",
        y_axis: str | None = None,
        trace_kwargs: dict[str, Any] | None = None,
        layout_kwargs: dict[str, Any] | None = None,
        uptake_conversion_factor: float | None = None,
        show: bool = False,
    ) -> Figure:
        """Plot an isotherm (stable + metastable gas and / or liquid) and group all traces under a single legend entry.

        You can pass any kwargs through `trace_kwargs` or `layout_kwargs`; missing values will be filled in by defaults.
        """
        import plotly.colors as pc
        import plotly.graph_objects as go

        if fig is None:
            fig = go.Figure()

        trace_kwargs = trace_kwargs or {}
        layout_kwargs = layout_kwargs or {}

        # look for an explicit color in trace_kwargs
        explicit_color = None
        if "line" in trace_kwargs and isinstance(trace_kwargs["line"], dict):
            explicit_color = trace_kwargs["line"].get("color")

        if explicit_color:
            color = explicit_color
        else:
            default_colors = pc.qualitative.Vivid
            calls = getattr(fig, "_plot_calls", 0)
            color = default_colors[calls % len(default_colors)]
            fig._plot_calls = calls + 1

        x_vals, x_title = self._resolve_x_axis(x_axis)
        y_axis = y_axis or self.uptake_unit
        y_factor = self._uptake_conversion_factor(y_axis, uptake_conversion_factor)

        legend_name = label or "Uptake"
        legendgroup = f"asaf-isotherm-{getattr(fig, '_asaf_isotherm_groups', 0)}"
        fig._asaf_isotherm_groups = getattr(fig, "_asaf_isotherm_groups", 0) + 1
        lg = dict(legendgroup=legendgroup)

        default_stable = {
            "x": x_vals,
            "y": self.amount_adsorbed * y_factor,
            "mode": "lines+markers",
            "name": legend_name,
            "line": dict(color=color),
            "marker": dict(
                color=color,
                symbol=trace_kwargs.get("marker", {}).get("symbol", "circle"),
            ),
            **lg,
        }

        user_line = trace_kwargs.get("line", {})
        user_marker = trace_kwargs.get("marker", {})

        stable_line = {**default_stable["line"], **user_line}
        stable_marker = {**default_stable["marker"], **user_marker}

        merged_stable = {
            **default_stable,
            **trace_kwargs,
            "line": stable_line,
            "marker": stable_marker,
        }

        fig.add_trace(go.Scatter(**merged_stable))

        # metastable defaults: just dashed line, no markers, and no extra legend entry
        default_meta = {
            "x": x_vals,
            "mode": "lines",
            "name": legend_name,
            "line": dict(color=color, dash="dash"),
            "showlegend": False,
            **lg,
        }

        meta_trace_kwargs = {**default_meta, **trace_kwargs}

        if self.metastable_gas is not None:
            gas_line = {**default_meta["line"], **user_line, "dash": "dash"}
            fig.add_trace(
                go.Scatter(
                    y=self.metastable_gas * y_factor,
                    **{**meta_trace_kwargs, "line": gas_line},
                )
            )
        if self.metastable_liq is not None:
            liq_line = {**default_meta["line"], **user_line, "dash": "dot"}
            fig.add_trace(
                go.Scatter(
                    y=self.metastable_liq * y_factor,
                    **{**meta_trace_kwargs, "line": liq_line},
                )
            )

        base_layout = dict(
            font=dict(family="Helvetica Neue", size=14, color="black"),
            xaxis=dict(
                showline=True,
                linewidth=1,
                linecolor="black",
                gridcolor="lightgrey",
                mirror=True,
                zeroline=False,
                ticks="inside",
                title=x_title,
            ),
            yaxis=dict(
                showline=True,
                linewidth=1,
                linecolor="black",
                gridcolor="lightgrey",
                mirror=True,
                zeroline=False,
                ticks="inside",
                title=f"Uptake ({y_axis})",
            ),
            plot_bgcolor="white",
            width=700,
            height=500,
            margin=dict(l=30, r=30, t=30, b=30),
            legend=dict(traceorder="grouped"),
        )
        fig.update_layout(**{**base_layout, **layout_kwargs})

        if show:
            fig.show()

        return fig

    def to_aif(
        self, filename: str, user_key_mapper: dict[str, Any] | None = None
    ) -> None:
        """Save the isotherm in an AIF file format.

        Parameters
        ----------
        filename
            The name of the file to be saved.
        user_key_mapper
            A dictionary based on which keys from the metadata are transformed into keys
            according to aifdictionary.json. Required format: {'_AIF_key': 'metadata_key'}.

        Returns
        -------
        None
        """
        from gemmi import cif

        metadata = self.metadata
        key_mapper = {
            "_exptl_temperature": "temperature",
            "_units_temperature": "temperature_units",
            "_adsnt_material_id": "framework_name",
            "_exptl_adsorptive_name": "molecule_name",
            "_simltn_code": "code_name",
            "_simltn_date": "simulation_date",
            "_simltn_size": "system_size",
            "_simltn_forcefield_adsorptive": "molecule_force_field",
            "_simltn_forcefield_adsorbent": "framework_force_field",
            "_units_pressure": "pressure_units",
            "_units_fugacity": "fugacity_units",
            "_units_loading": "loading_units",
        }

        if user_key_mapper:
            key_mapper.update(user_key_mapper)

        doc = cif.Document()
        doc.add_new_block("isotherm")
        block = doc.sole_block()

        if metadata:
            for key, value in key_mapper.items():
                if value in metadata.keys():
                    if isinstance(metadata[value], (int, float)):
                        block.set_pair(key, str(metadata[value]))
                    else:
                        block.set_pair(key, quote(metadata[value]))

        block.set_pair("_units_loading", quote(self.uptake_unit))
        block.set_pair("_audit_aif_version", quote("63df4e8"))

        df = self.dataframe.copy()
        column_map = (
            ("pressure", "pressure"),
            ("fugacity", "fugacity"),
            ("p/p0", "relative_pressure"),
            ("f/f0", "relative_fugacity"),
            ("relative_humidity", "relative_humidity"),
            ("relative humidity", "relative_humidity"),
            ("RH", "relative_humidity"),
            ("rh", "relative_humidity"),
            ("metastable_gas", "amount_metastable_gas"),
            ("metastable_liq", "amount_metastable_liq"),
        )

        loop_columns = []
        loop_tags = []
        for column, tag in column_map:
            if column in df.columns:
                loop_columns.append(column)
                loop_tags.append(tag)

        if self.saturation_pressure is not None and "pressure" in df.columns:
            df["saturation_pressure"] = self.saturation_pressure
            loop_columns.append("saturation_pressure")
            loop_tags.append("p0")

        if self.saturation_fugacity is not None and "fugacity" in df.columns:
            df["saturation_fugacity"] = self.saturation_fugacity
            loop_columns.append("saturation_fugacity")
            loop_tags.append("f0")

        if "uptake" not in loop_columns:
            loop_columns.append("uptake")
            loop_tags.append("amount")

        if len(loop_columns) == 1:
            raise ValueError(
                "AIF export requires at least one pressure-related column in addition to 'uptake'."
            )

        loop_ads = block.init_loop("_adsorp_", loop_tags)
        loop_ads.set_all_values(
            [list(df[column].values.astype(str)) for column in loop_columns]
        )

        if filename.endswith(".aif"):
            filename = filename[:-4]
        doc.write_file(f"{filename}.aif")

    def to_csv(self, filename: str) -> None:
        """Save the isotherm data to a CSV file."""
        self.dataframe.to_csv(filename, index=False)
