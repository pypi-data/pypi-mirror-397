"""
Main mathematical operations module for fixed-point arithmetic.

This module provides basic arithmetic operations using fixed-point
numbers (Fx) along with utility functions for mathematical calculations.
"""

from __future__ import annotations
from metrima.core.fixed import Fx, fx

def _make_divider(divisor: str = "-",
                  count: int = 60) -> str:
    """
    Create a divider string for output formatting.
    
    :param divisor: Character to use for the divider.
    :type divisor: str
    :param count: Number of times to repeat the divisor character.
    :type count: int
    :return: Divider string.
    :rtype: str
    """
    return divisor*count

def add(a: int | float | Fx,
        b: int | float | Fx) -> int | float | Fx:
    """
    Add two numbers.
    
    :param a: First number to add.
    :type a: int | float | Fx
    :param b: Second number to add.
    :type b: int | float | Fx
    :return: Sum of a and b.
    :rtype: int | float | Fx
    """
    if isinstance(a, float):
        a = fx(a)
    if isinstance(b, float):
        b = fx(b)
    return a + b

def subtract(a: int | float | Fx,
             b: int | float | Fx) -> int | float | Fx:
    """
    Subtract two numbers.
    
    :param a: Number to subtract from.
    :type a: int | float | Fx
    :param b: Number to subtract.
    :type b: int | float | Fx
    :return: Difference of a and b.
    :rtype: int | float | Fx
    """
    if isinstance(a, float):
        a = fx(a)
    if isinstance(b, float):
        b = fx(b)
    return a - b

def mul(a: int | float | Fx,
        b: int | float | Fx) -> int | float | Fx:
    """
    Multiply two numbers.
    
    :param a: First number to multiply.
    :type a: int | float | Fx
    :param b: Second number to multiply.
    :type b: int | float | Fx
    :return: Product of a and b.
    :rtype: int | float | Fx
    """
    if isinstance(a, float):
        a = fx(a)
    if isinstance(b, float):
        b = fx(b)
    return a * b

def div(a: int | float | Fx,
        b: int | float | Fx) -> int | float | Fx:
    """
    Divide two numbers.
    
    :param a: Numerator.
    :type a: int | float | Fx
    :param b: Denominator.
    :type b: int | float | Fx
    :return: Quotient of a divided by b.
    :rtype: int | float | Fx
    :raises ZeroDivisionError: If b is zero.
    """
    if isinstance(a, float):
        a = fx(a)
    if isinstance(b, float):
        b = fx(b)
    if b != 0:
        return a / b
    raise ZeroDivisionError

def sigma(collection: list[Fx] | list[int] | list[float]) -> Fx:
    """
    Sum of all elements in a collection.
    
    :param collection: Collection of numbers to sum.
    :type collection: list[Fx] | list[int] | list[float]
    :return: Sum of all elements in the collection.
    :rtype: Fx
    """
    return_result: int = 0
    for i in collection:
        return_result += i # type: ignore
    return fx(return_result)

def sigma_noiter(*numbers: Fx | int | float) -> Fx:
    """
    Sum of all provided numbers without using an iterable.
    
    :param numbers: Numbers to sum.
    :type numbers: Fx | int | float
    :return: Sum of all provided numbers.
    :rtype: Fx
    """
    return_result: Fx = Fx(0)
    for i in numbers:
        i = fx(i)
        return_result += i
    return return_result

def power(base: int | float | Fx,
          exp: int | float | Fx) -> int | float | Fx:
    """
    Raise `base` to the power of `exp`.
    
    :param base: Number to be raised.
    :type base: int | float | Fx
    :param exp: Exponent.
    :type exp: int | float | Fx
    :return: Result of base raised to exp.
    :rtype: int | float | Fx
    """
    if isinstance(base, (int, float)):
        base = fx(base)
    if isinstance(exp, (int, float)):
        exp = fx(exp)
    return base ** exp

def largest(collection: list[Fx] | list[int] | list[float]) -> Fx | int | float:
    """
    Get the maximum value from a collection.
    
    :param collection: Collection to get maximum from.
    :type collection: list[Fx] | list[int] | list[float]
    :return: Maximum value in the collection.
    :rtype: Fx | int | float
    """
    max_value: Fx = fx(collection[0])
    for i in collection:
        if i > max_value:
            max_value = fx(i)
    return max_value

def smallest(collection: list[Fx] | list[int] | list[float]) -> Fx | int | float:
    """
    Get the minimum value from a collection.
    
    :param collection: Collection to get minimum from.
    :type collection: list[Fx] | list[int] | list[float]
    :return: Minimum value in the collection.
    :rtype: Fx | int | float
    """
    min_value: Fx = fx(collection[0])
    for i in collection:
        if i < min_value:
            min_value = fx(i)
    return min_value


if __name__ == "__main__":
    from ..tests import test_main
    test_main()