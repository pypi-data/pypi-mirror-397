"""
Units module for measurement conversions and operations.

This module provides classes and functions for working with various
measurement units including time, weight, and conversion utilities.
"""

from .utils import downgrade_float_fx, ImperialUnit, MetricUnit
from .time import Hour, hour, Minute, minute, Second, second, Millisecond, ms
from .weight import (WeightUnit, ImperialWeightUnit, MetricWeightUnit, Kilogram, 
                     Gram, Milligram, Microgram, Pound, Ounce, Ton, Tonne, Grain, 
                     kg, gram, mg, mcg, lb, oz, grain)

__all__ = [
    "Hour",
    "Minute",
    "Second",
    "Millisecond",
    "second",
    "minute",
    "hour",
    "ms",

    "downgrade_float_fx",
    "ImperialUnit",
    "MetricUnit",

    "WeightUnit", "ImperialWeightUnit", "MetricWeightUnit", "Kilogram", 
    "Gram", "Milligram", "Microgram", "Pound", "Ounce", "Ton", "Tonne", "Grain", 
    "kg", "gram", "mg", "mcg", "lb", "oz", "grain",
]