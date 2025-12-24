"""
Metrima Package Initialization.

This module exports the core functionality of the Metrima library, including
mathematical operations, unit conversions, and utility functions.

Attributes:
    __version__ (str): The current version of the Metrima library.
    __author__ (str): The author of the library.
"""

from .lib import length, is_whole, is_whitespace, span, push_back, attach, locate, invert, trim, has, combinelst, duplicate, verify, chop

from . import units
from . import utils
from . import math
from . import core

__all__ = [
    "utils",
    "units",
    "math",
    "core",
    "length",
    "is_whole",
    "is_whitespace",
    "span",
    "push_back",
    "attach",
    "locate",
    "invert",
    "trim",
    "has",
    "combinelst",
    "duplicate",
    "verify",
    "chop",
]

__version__ = "0.3.5.3"
__author__ = "Razka Rizaldi"