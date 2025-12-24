"""
Physical and mathematical constants for use throughout the application.

This module provides commonly used mathematical and physical constants
as final (immutable) values for consistent calculations.
"""

from typing import Final

PI: Final[float] = 3.1415926535
"""The mathematical constant π (pi)."""

E: Final[float] = 2.7182818284
"""The mathematical constant e (Euler's number)."""

GRAVITY: Final[float] = 9.80665  # m/s^2
"""Standard acceleration due to gravity on Earth."""

SPEED_OF_LIGHT: Final[int] = 299792458  # m/s
"""Speed of light in a vacuum."""

PLANCK_CONSTANT: Final[float] = 6.62607015e-34  # Js
"""Planck constant (h)."""

BOLTZMANN_CONSTANT: Final[float] = 1.380649e-23  # J/K
"""Boltzmann constant."""

AVOGADRO_NUMBER: Final[float] = 6.02214076e23  # 1/mol
"""Avogadro's number."""

GAS_CONSTANT: Final[float] = 8.314462618  # J/(mol·K)
"""Universal gas constant."""

GOLDEN_RATIO: Final[float] = 1.6180339887
"""The golden ratio (φ)."""

INFINITE: Final[float] = float('inf')
"""Positive infinity value."""

NAN: Final[float] = float('nan')
"""Not-a-Number value."""