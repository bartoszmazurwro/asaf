"""ASAF: A library for adsorption simulation and analysis in porous materials."""

import logging
from importlib.metadata import PackageNotFoundError, version

from .constants import ForceFieldParameters
from .framework import Framework
from .isotherm import Isotherm
from .mpd import MPD

logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    __version__ = version("asaf")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "Framework",
    "Isotherm",
    "MPD",
    "ForceFieldParameters",
    "__version__",
]
