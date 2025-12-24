"""
Custom exception classes for the Metrima library.

This module defines various exception types used throughout the library
to provide more specific error handling.
"""

from __future__ import annotations

class UnexpectedTypeError(Exception):
    """
    Exception raised when an unexpected type is encountered.
    
    This error is used when a function or method receives an argument
    of an incorrect or unexpected type.
    """
    pass

class MissingArgument(Exception):
    """
    Exception raised when a required argument is missing.
    
    This error is used when a function or method is called without
    a required argument.
    """
    pass

class ConstantError(Exception):
    """
    Exception raised when attempting to modify a constant value.
    
    :param message: Custom error message.
    :type message: str
    """
    def __init__(self, message: str = "Cannot modify a constant") -> None:
        super().__init__(message)

class DimensionError(Exception):
    """
    Custom error raised when an invalid unit conversion is attempted.
    
    :param unit_a: First unit in the invalid operation.
    :type unit_a: Any
    :param unit_b: Second unit in the invalid operation.
    :type unit_b: Any
    :param message: Custom error message.
    :type message: str | None
    """
    def __init__(self, unit_a, unit_b, message: str | None = None):
        self.unit_a = unit_a
        self.unit_b = unit_b

        class_a = type(unit_a).__name__
        class_b = type(unit_b).__name__

        if message is None:
            message = (
                f"Attempted to execute an operation between incompatible unit dimensions: "
                f"'{class_a}' and '{class_b}'. "
                f"Check that both units belong to the same system (Weight, Distance, Time, Temperature) "
            )

        super().__init__(message)