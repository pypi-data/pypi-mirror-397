# type: ignore
from __future__ import annotations
# type: ignore # gets rid of mypy false positives
from metrima.utils.errors import UnexpectedTypeError

class Fx:
    """
    A fixed-point decimal number class for precise decimal arithmetic.
    
    :param value: The initial value to create the Fx object from.
    :type value: Fx | str | float | int
    """
    def __init__(self, value: 'Fx' | str | float | int) -> None:
        if isinstance(value, Fx):
            self.value: int = value.value
            self.scale: int = value.scale
            return
        s = str(value)
        if '.' in s:
            whole, frac = s.split('.')
            self.scale = len(frac)
            self.value = int(whole + frac)
        else:
            self.scale = 0
            self.value = int(s)

        self._normalize()

    def is_zero(self) -> bool:
        """
        Check if the number is exactly zero.
        
        :return: True if the number is zero, False otherwise.
        :rtype: bool
        """
        return int(self.value) == 0

    def is_positive(self) -> bool:
        """
        Check if the number is greater than zero.
        
        :return: True if the number is positive, False otherwise.
        :rtype: bool
        """
        return int(self.value) > 0

    def is_negative(self) -> bool:
        """
        Check if the number is less than zero.
        
        :return: True if the number is negative, False otherwise.
        :rtype: bool
        """
        return int(self.value) < 0

    def copy(self) -> 'Fx':
        """
        Create a shallow copy of the Fx object.
        
        :return: A new Fx instance with the same value and scale.
        :rtype: Fx
        """
        new_copy = Fx.__new__(Fx)
        new_copy.value = self.value
        new_copy.scale = self.scale
        return new_copy

    def _normalize(self):
        """Remove trailing zeros from the fractional part"""
        if self.value == 0:
            self.scale = 0
            return

        while self.scale > 0 and self.value % 10 == 0:
            self.value //= 10
            self.scale -= 1

    def _align(self, other: 'Fx') -> tuple[int, int, int]:
        """
        Align two Fx objects to the same scale for arithmetic operations.
        
        :param other: The other Fx object to align with.
        :type other: Fx
        :return: Tuple containing (self_value_aligned, other_value_aligned, common_scale)
        :rtype: tuple[int, int, int]
        :raises UnexpectedTypeError: If other is not an Fx instance.
        """
        if not isinstance(other, Fx):
            raise UnexpectedTypeError(f"Unexpected type {type(other)}")

        if self.scale == other.scale:
            return self.value, other.value, self.scale
        if self.scale > other.scale:
            diff = self.scale - other.scale
            return self.value, other.value * (10 ** diff), self.scale
        diff = other.scale - self.scale
        return self.value * (10 ** diff), other.value, other.scale

    def __repr__(self):
        """
        Return the official string representation of the Fx object.
        
        :return: String representation showing value and scale.
        :rtype: str
        """
        return f"Fx(value={self.value}, scale={self.scale})"

    def __hash__(self):
        """
        Return a hash value for the Fx object.
        
        :return: Hash value based on value and scale.
        :rtype: int
        """
        return hash((self.value, self.scale))

    #--- Conversions ---#
    def __float__(self):
        """
        Convert the Fx object to a floating-point number.
        
        :return: Floating-point representation of the number.
        :rtype: float
        """
        return self.value / (10 ** self.scale)

    def __int__(self):
        """
        Convert the Fx object to an integer.
        
        :return: Integer representation (truncates fractional part).
        :rtype: int
        """
        return int(float(self))

    def __str__(self):
        """
        Return a string representation of the Fx object.
        
        :return: String representation of the decimal number.
        :rtype: str
        """
        if self.scale == 0:
            return str(self.value)

        sign = "-" if self.value < 0 else ""
        val_str = str(abs(self.value))

        val_str = val_str.zfill(self.scale + 1)

        integer_part = val_str[:-self.scale]
        fractional_part = val_str[-self.scale:]

        return f"{sign}{integer_part}.{fractional_part}"

    #--- Miscellaneous ---#
    def __neg__(self) -> 'Fx':
        """
        Return the negation of the Fx object.
        
        :return: Negative of the current number.
        :rtype: Fx
        """
        result = Fx.__new__(Fx)
        result.value = -self.value
        result.scale = self.scale
        result._normalize()
        return result

    def __pos__(self) -> 'Fx':
        """
        Return the positive of the Fx object.
        
        :return: Positive of the current number.
        :rtype: Fx
        """
        result = Fx.__new__(Fx)
        result.value = self.value
        result.scale = self.scale
        result._normalize()
        return result

    def __abs__(self) -> 'Fx':
        """
        Return the absolute value of the Fx object.
        
        :return: Absolute value of the current number.
        :rtype: Fx
        """
        result = Fx.__new__(Fx)
        result.value = abs(self.value)
        result.scale = self.scale
        result._normalize()
        return result

    def __round__(self, n: int = 0) -> 'Fx':
        """
        Round the Fx object to n decimal places.
        
        :param n: Number of decimal places to round to.
        :type n: int
        :return: Rounded Fx object.
        :rtype: Fx
        """
        return Fx(round(float(self), n))

    def __index__(self) -> int:
        """
        Convert the Fx object to an integer for indexing.
        
        :return: Integer representation for indexing.
        :rtype: int
        """
        return int(self)

    def __format__(self, format_spec: str) -> str:
        """
        Format the Fx object using the given format specification.
        
        :param format_spec: Format specification string.
        :type format_spec: str
        :return: Formatted string.
        :rtype: str
        """
        return format(float(self), format_spec)

    #--- Comparisons ---#
    def _to_fx(self, other):
        """
        Convert non-Fx types to Fx for safe comparison/arithmetic.
        
        :param other: Value to convert to Fx.
        :type other: Any
        :return: Fx representation of other.
        :rtype: Fx
        :raises NotImplementedError: If conversion is not possible.
        """
        if isinstance(other, Fx):
            return other
        if isinstance(other, (int, float, str)):
            return fx(other)
        raise NotImplementedError

    def __eq__(self, other):
        """
        Check if two values are equal.
        
        :param other: Value to compare with.
        :type other: Any
        :return: True if equal, False otherwise.
        :rtype: bool
        """
        other = self._to_fx(other)
        if other is NotImplemented: return False
        a, b, _ = self._align(other)
        return a == b

    def __ne__(self, other):
        """
        Check if two values are not equal.
        
        :param other: Value to compare with.
        :type other: Any
        :return: True if not equal, False otherwise.
        :rtype: bool
        """
        other = self._to_fx(other)
        if other is NotImplemented: return True
        a, b, _ = self._align(other)
        return a != b

    def __gt__(self, other):
        """
        Check if self is greater than other.
        
        :param other: Value to compare with.
        :type other: Any
        :return: True if greater, NotImplemented if comparison fails.
        :rtype: bool | NotImplemented
        """
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        a, b, _ = self._align(other)
        return a > b

    def __ge__(self, other):
        """
        Check if self is greater than or equal to other.
        
        :param other: Value to compare with.
        :type other: Any
        :return: True if greater or equal, NotImplemented if comparison fails.
        :rtype: bool | NotImplemented
        """
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        a, b, _ = self._align(other)
        return a >= b

    def __lt__(self, other):
        """
        Check if self is less than other.
        
        :param other: Value to compare with.
        :type other: Any
        :return: True if less, NotImplemented if comparison fails.
        :rtype: bool | NotImplemented
        """
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        a, b, _ = self._align(other)
        return a < b

    def __le__(self, other):
        """
        Check if self is less than or equal to other.
        
        :param other: Value to compare with.
        :type other: Any
        :return: True if less or equal, NotImplemented if comparison fails.
        :rtype: bool | NotImplemented
        """
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        a, b, _ = self._align(other)
        return a <= b

    # --- Arithmetics ---#
    def __add__(self, other: 'Fx' | float | int) -> 'Fx':
        """
        Add two values.
        
        :param other: Value to add.
        :type other: Fx | float | int
        :return: Sum of self and other.
        :rtype: Fx
        """
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        a, b, scale = self._align(other)
        result_value = a + b
        result = Fx.__new__(Fx)
        result.value = result_value
        result.scale = scale
        result._normalize()
        return result

    def __sub__(self, other: 'Fx' | float | int) -> 'Fx':
        """
        Subtract other from self.
        
        :param other: Value to subtract.
        :type other: Fx | float | int
        :return: Difference of self and other.
        :rtype: Fx
        """
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        a, b, scale = self._align(other)
        result_value = a - b
        result = Fx.__new__(Fx)
        result.value = result_value
        result.scale = scale
        result._normalize()
        return result

    def __mul__(self, other: 'Fx' | float | int) -> 'Fx':
        """
        Multiply two values.
        
        :param other: Value to multiply by.
        :type other: Fx | float | int
        :return: Product of self and other.
        :rtype: Fx
        """
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        result_value = self.value * other.value
        scale = self.scale + other.scale
        result = Fx.__new__(Fx)
        result.value = result_value
        result.scale = scale
        result._normalize()
        return result

    def __truediv__(self, other: 'Fx' | float | int) -> 'Fx':
        """
        Divide self by other.
        
        :param other: Value to divide by.
        :type other: Fx | float | int
        :return: Quotient of self divided by other.
        :rtype: Fx
        :raises ZeroDivisionError: If other is zero.
        """
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        if other.value == 0:
            raise ZeroDivisionError

        a, b, _ = self._align(other)

        calc_precision = max(16, self.scale + other.scale + 4)

        numerator = a * (10 ** calc_precision)

        result_value = numerator // b
        result_scale = calc_precision

        result = Fx.__new__(Fx)
        result.value = result_value
        result.scale = result_scale
        result._normalize()
        return result

    def __floordiv__(self, other: 'Fx' | float | int) -> 'Fx':
        """
        Floor divide self by other.
        
        :param other: Value to divide by.
        :type other: Fx | float | int
        :return: Floor quotient of self divided by other.
        :rtype: Fx
        :raises ZeroDivisionError: If other is zero.
        """
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        if other.value == 0:
            raise ZeroDivisionError

        a, b, _ = self._align(other)

        result_value = a // b

        result = Fx.__new__(Fx)
        result.value = result_value
        result.scale = 0
        result._normalize()
        return result

    def __pow__(self, other: 'Fx' | float | int) -> 'Fx':
        """
        Raise self to the power of other.
        
        :param other: Exponent.
        :type other: Fx | float | int
        :return: self raised to the power of other.
        :rtype: Fx
        """
        if isinstance(other, (int, float)):
            other = fx(other)
        if not isinstance(other, Fx):
            return NotImplemented

        exponent = float(other)
        base = self

        if other.scale == 0 and other.value >= 0:
            exp_int = other.value
            if exp_int == 0:
                return Fx(1)
            result = Fx(1)
            for _ in range(exp_int):
                result *= base
            return result

        else:
            base_float = float(base)
            result_float = base_float ** exponent
            return Fx(result_float)

    def __mod__(self, other: 'Fx' | float | int) -> 'Fx':
        """
        Compute the modulus of self divided by other.
        
        :param other: Value to compute modulus with.
        :type other: Fx | float | int
        :return: Remainder of self divided by other.
        :rtype: Fx
        """
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented

        a, b, scale = self._align(other)

        result_value = a % b

        result = Fx.__new__(Fx)
        result.value = result_value
        result.scale = scale
        result._normalize()
        return result

    # --- Right hand operations ---#
    def __radd__(self, other: int | float) -> 'Fx':
        """
        Right-hand addition.
        
        :param other: Value to add to self.
        :type other: int | float
        :return: Sum of other and self.
        :rtype: Fx
        """
        return self + other

    def __rsub__(self, other: int | float) -> 'Fx':
        """
        Right-hand subtraction.
        
        :param other: Value to subtract self from.
        :type other: int | float
        :return: Difference of other minus self.
        :rtype: Fx
        """
        return fx(other) - self

    def __rmul__(self, other: int | float) -> 'Fx':
        """
        Right-hand multiplication.
        
        :param other: Value to multiply by self.
        :type other: int | float
        :return: Product of other and self.
        :rtype: Fx
        """
        return self * other

    def __rtruediv__(self, other: int | float) -> 'Fx':
        """
        Right-hand true division.
        
        :param other: Value to divide by self.
        :type other: int | float
        :return: Quotient of other divided by self.
        :rtype: Fx
        """
        return fx(other) / self

    def __rfloordiv__(self, other: int | float) -> 'Fx':
        """
        Right-hand floor division.
        
        :param other: Value to floor divide by self.
        :type other: int | float
        :return: Floor quotient of other divided by self.
        :rtype: Fx
        """
        return fx(other) // self

    def __rmod__(self, other: int | float) -> 'Fx':
        """
        Right-hand modulus.
        
        :param other: Value to compute modulus with self.
        :type other: int | float
        :return: Remainder of other divided by self.
        :rtype: Fx
        """
        return fx(other) % self

    def __rpow__(self, other: int | float) -> 'Fx':
        """
        Right-hand exponentiation.
        
        :param other: Base value.
        :type other: int | float
        :return: other raised to the power of self.
        :rtype: Fx
        """
        return fx(other) ** self

    def is_integer(self) -> bool:
        """
        Check if the Fx number represents an integer value.
        
        :return: True if the number has no fractional part, False otherwise.
        :rtype: bool
        """
        return self.scale == 0


def fx(value: Fx | str | int | float) -> Fx:
    """
    Convert a value to an Fx object.
    
    :param value: The value to convert.
    :type value: Fx | str | int | float
    :return: Fx representation of the value.
    :rtype: Fx
    """
    return Fx(value)

if __name__ == "__main__":
    from ..tests import test_fx
    test_fx()