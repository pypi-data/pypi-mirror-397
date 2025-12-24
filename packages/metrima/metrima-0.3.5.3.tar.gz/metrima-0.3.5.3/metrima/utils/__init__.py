"""
Metrima utilities package initialization.

This package provides various utility functions, decorators, and error classes
for the Metrima library.
"""

from .center_text import center_text
from .decorators import mimic, memo, repeat, timed, legacy, attribute, once
from .errors import UnexpectedTypeError, MissingArgument, ConstantError
from .exists import exists

__all__ = [
    "UnexpectedTypeError",
    "MissingArgument",
    "ConstantError",

    "center_text",

    "legacy",
    "timed", 
    "repeat", 
    "memo", 
    "mimic",
    "once",
    "attribute",

    "exists",
]