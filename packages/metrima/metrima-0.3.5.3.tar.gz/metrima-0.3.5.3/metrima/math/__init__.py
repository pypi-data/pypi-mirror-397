"""
Main package initialization for mathematical operations and constants.

This module exports the core mathematical functions and constants
for use throughout the application.
"""

from .main import _make_divider, add, subtract, mul, div, sigma, sigma_noiter
from .constants import PI, E, GOLDEN_RATIO, GRAVITY, SPEED_OF_LIGHT, PLANCK_CONSTANT, BOLTZMANN_CONSTANT, AVOGADRO_NUMBER, GAS_CONSTANT, INFINITE, NAN

__all__ = [
    "_make_divider",
    "add",
    "subtract",
    "mul",
    "div",
    "sigma",
    "sigma_noiter",

    "PI",
    "E",
    "GOLDEN_RATIO",
    "GRAVITY",
    "SPEED_OF_LIGHT",
    "PLANCK_CONSTANT",
    "BOLTZMANN_CONSTANT",
    "AVOGADRO_NUMBER",
    "GAS_CONSTANT",
    "INFINITE",
    "NAN",
]