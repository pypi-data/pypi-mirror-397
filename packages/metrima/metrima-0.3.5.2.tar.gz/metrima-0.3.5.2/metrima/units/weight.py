"""
Weight unit classes for representing and converting between different weight/mass units.

This module provides classes for both metric (microgram through tonne) and imperial
(grain through ton) weight units with full arithmetic operations and conversions.
"""

from typing import Union
from typing_extensions import TypeAlias

from metrima.core.fixed import Fx, fx
from metrima.core.temporary import Temporary, temp
from metrima.units.utils import ImperialUnit, MetricUnit, downgrade_float_fx
from metrima.utils.errors import DimensionError

def snap(val):
    """
    Snap a value to the nearest integer if very close.
    
    :param val: Value to snap.
    :type val: int | float | Fx
    :return: Original value or nearest integer if within tolerance.
    :rtype: int | float | Fx
    """
    if isinstance(val, (int, float, Fx)):
        val_float = float(val) 
        nearest = round(val_float)
        if abs(val_float - nearest) < 1e-9: 
            return nearest
    return val

def is_cross_system(cls, other) -> bool:
    """
    Check if two units belong to different measurement systems.
    
    :param cls: First unit instance.
    :type cls: Any
    :param other: Second unit instance.
    :type other: Any
    :return: True if units are from different systems (metric/imperial), False otherwise.
    :rtype: bool
    """
    return (
        (isinstance(cls, MetricUnit) and isinstance(other, ImperialUnit))
        or
        (isinstance(cls, ImperialUnit) and isinstance(other, MetricUnit))
    )

class WeightUnit:
    """
    Base class for all weight/mass units.
    
    Provides a unified interface for weight conversions and arithmetic operations
    between metric and imperial systems. All weight units inherit from this class
    and implement the conversion protocol methods.
    """
    
    def __init__(self, value: 'NumericInput | WeightUnit') -> None:
        """
        Initialize a weight unit.
        
        :param value: Numeric value or another WeightUnit instance to convert from.
        :type value: NumericInput | WeightUnit
        """
        self.raw_value = value
        self._process_value()
    
    def _process_value(self) -> None:
        """
        Process the raw input value according to the specific unit class.
        
        Subclasses must implement this method to handle conversion and storage
        of the value in the appropriate format.
        
        :raises NotImplementedError: If called on base class.
        """
        self.value = fx(self.raw_value) # type: ignore
        raise NotImplementedError

    def __microgram__(self) -> Fx:
        """
        Convert to micrograms.
        
        :return: Weight value in micrograms.
        :rtype: Fx
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError

    def __milligram__(self) -> Fx:
        """
        Convert to milligrams.
        
        :return: Weight value in milligrams.
        :rtype: Fx
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError
    
    def __gram__(self) -> Fx:
        """
        Convert to grams.
        
        :return: Weight value in grams.
        :rtype: Fx
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError
    
    def __kilogram__(self) -> Fx:
        """
        Convert to kilograms.
        
        :return: Weight value in kilograms.
        :rtype: Fx
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError

    def __tonne__(self) -> Fx:
        """
        Convert to tonnes (metric tons).
        
        :return: Weight value in tonnes.
        :rtype: Fx
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError

    def __grain__(self) -> Fx:
        """
        Convert to grains.
        
        :return: Weight value in grains.
        :rtype: Fx
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError

    def __ounce__(self) -> Fx:
        """
        Convert to ounces.
        
        :return: Weight value in ounces.
        :rtype: Fx
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError

    def __pound__(self) -> Fx:
        """
        Convert to pounds.
        
        :return: Weight value in pounds.
        :rtype: Fx
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError
    
    def __ton__(self) -> Fx:
        """
        Convert to imperial long tons.
        
        :return: Weight value in long tons.
        :rtype: Fx
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError
    
    def __add__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Add two weights.
        
        Returns result in kilograms for metric-metric or cross-system operations,
        or pounds for imperial-imperial operations.
        
        :param other: Weight to add.
        :type other: WeightUnit
        :return: New WeightUnit with sum.
        :rtype: WeightUnit
        :raises DimensionError: If other is not a WeightUnit.
        """
        if not isinstance(other, WeightUnit):
            raise DimensionError(self, other)

        if isinstance(self, MetricWeightUnit) and isinstance(other, MetricWeightUnit):
            return kg(self.__kilogram__() + other.__kilogram__())
        elif isinstance(self, ImperialWeightUnit) and isinstance(other, ImperialWeightUnit):
            return lb(self.__pound__() + other.__pound__())
        
        if is_cross_system(self, other=other):
            return kg(self.__kilogram__() + other.__kilogram__())
        
        return WeightUnit(0)  # Fallback, should not reach here.
        
    def __radd__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Right-hand addition (other + self).
        
        :param other: Weight to add.
        :type other: WeightUnit
        :return: New WeightUnit with sum.
        :rtype: WeightUnit
        """
        return self.__add__(other)
    
    def __sub__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Subtract two weights.
        
        Returns result in kilograms for metric-metric or cross-system operations,
        or pounds for imperial-imperial operations.
        
        :param other: Weight to subtract.
        :type other: WeightUnit
        :return: New WeightUnit with difference.
        :rtype: WeightUnit
        :raises DimensionError: If other is not a WeightUnit.
        """
        if not isinstance(other, WeightUnit):
            raise DimensionError(self, other)

        if isinstance(self, MetricWeightUnit) and isinstance(other, MetricWeightUnit):
            return kg(self.__kilogram__() - other.__kilogram__())
        elif isinstance(self, ImperialWeightUnit) and isinstance(other, ImperialWeightUnit):
            return lb(self.__pound__() - other.__pound__())
        
        if is_cross_system(self, other=other):
            return kg(self.__kilogram__() - other.__kilogram__())
        
        return WeightUnit(0)  # Fallback, should not reach here.
        
    def __rsub__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Right-hand subtraction (other - self).
        
        :param other: Weight to subtract from.
        :type other: WeightUnit
        :return: New WeightUnit with difference.
        :rtype: WeightUnit
        """
        return self.__sub__(other)
    
    def __mul__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Multiply two weights.
        
        Returns result in kilograms for metric-metric or cross-system operations,
        or pounds for imperial-imperial operations.
        
        :param other: Weight to multiply by.
        :type other: WeightUnit
        :return: New WeightUnit with product.
        :rtype: WeightUnit
        :raises DimensionError: If other is not a WeightUnit.
        """
        if not isinstance(other, WeightUnit):
            raise DimensionError(self, other)

        if isinstance(self, MetricWeightUnit) and isinstance(other, MetricWeightUnit):
            return kg(self.__kilogram__() * other.__kilogram__())
        elif isinstance(self, ImperialWeightUnit) and isinstance(other, ImperialWeightUnit):
            return lb(self.__pound__() * other.__pound__())
        
        if is_cross_system(self, other=other):
            return kg(self.__kilogram__() * other.__kilogram__())
        
        return WeightUnit(0)  # Fallback, should not reach here.
        
    def __rmul__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Right-hand multiplication (other * self).
        
        :param other: Weight to multiply by.
        :type other: WeightUnit
        :return: New WeightUnit with product.
        :rtype: WeightUnit
        """
        return self.__mul__(other)
    
    def __truediv__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Divide two weights.
        
        Returns result in kilograms for metric-metric or cross-system operations,
        or pounds for imperial-imperial operations.
        
        :param other: Weight to divide by.
        :type other: WeightUnit
        :return: New WeightUnit with quotient.
        :rtype: WeightUnit
        :raises DimensionError: If other is not a WeightUnit.
        """
        if not isinstance(other, WeightUnit):
            raise DimensionError(self, other)

        if isinstance(self, MetricWeightUnit) and isinstance(other, MetricWeightUnit):
            return kg(self.__kilogram__() / other.__kilogram__())
        elif isinstance(self, ImperialWeightUnit) and isinstance(other, ImperialWeightUnit):
            return lb(self.__pound__() / other.__pound__())
        
        if is_cross_system(self, other=other):
            return kg(self.__kilogram__() / other.__kilogram__())
        
        return WeightUnit(0)  # Fallback, should not reach here.
        
    def __rtruediv__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Right-hand division (other / self).
        
        :param other: Weight to divide.
        :type other: WeightUnit
        :return: New WeightUnit with quotient.
        :rtype: WeightUnit
        """
        return self.__truediv__(other)
    
    def __floordiv__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Floor divide two weights.
        
        Returns result in kilograms for metric-metric or cross-system operations,
        or pounds for imperial-imperial operations.
        
        :param other: Weight to divide by.
        :type other: WeightUnit
        :return: New WeightUnit with floor division result.
        :rtype: WeightUnit
        :raises DimensionError: If other is not a WeightUnit.
        """
        if not isinstance(other, WeightUnit):
            raise DimensionError(self, other)

        if isinstance(self, MetricWeightUnit) and isinstance(other, MetricWeightUnit):
            return kg(self.__kilogram__() // other.__kilogram__())
        elif isinstance(self, ImperialWeightUnit) and isinstance(other, ImperialWeightUnit):
            return lb(self.__pound__() // other.__pound__())
        
        if is_cross_system(self, other=other):
            return kg(self.__kilogram__() // other.__kilogram__())
        
        return WeightUnit(0)  # Fallback, should not reach here.
        
    def __rfloordiv__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Right-hand floor division (other // self).
        
        :param other: Weight to divide.
        :type other: WeightUnit
        :return: New WeightUnit with floor division result.
        :rtype: WeightUnit
        """
        return self.__floordiv__(other)
    
    def __pow__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Raise weight to a power.
        
        Returns result in kilograms for metric-metric or cross-system operations,
        or pounds for imperial-imperial operations.
        
        :param other: Weight exponent.
        :type other: WeightUnit
        :return: New WeightUnit with power result.
        :rtype: WeightUnit
        :raises DimensionError: If other is not a WeightUnit.
        """
        if not isinstance(other, WeightUnit):
            raise DimensionError(self, other)

        if isinstance(self, MetricWeightUnit) and isinstance(other, MetricWeightUnit):
            return kg(self.__kilogram__() ** other.__kilogram__())
        elif isinstance(self, ImperialWeightUnit) and isinstance(other, ImperialWeightUnit):
            return lb(self.__pound__() ** other.__pound__())
        
        if is_cross_system(self, other=other):
            return kg(self.__kilogram__() ** other.__kilogram__())
        
        return WeightUnit(0)  # Fallback, should not reach here.
        
    def __rpow__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Right-hand power (other ** self).
        
        :param other: Weight base.
        :type other: WeightUnit
        :return: New WeightUnit with power result.
        :rtype: WeightUnit
        """
        return self.__pow__(other)
    
    def __mod__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Modulo operation on two weights.
        
        Returns result in kilograms for metric-metric or cross-system operations,
        or pounds for imperial-imperial operations.
        
        :param other: Weight divisor.
        :type other: WeightUnit
        :return: New WeightUnit with modulo result.
        :rtype: WeightUnit
        :raises DimensionError: If other is not a WeightUnit.
        """
        if not isinstance(other, WeightUnit):
            raise DimensionError(self, other)

        if isinstance(self, MetricWeightUnit) and isinstance(other, MetricWeightUnit):
            return kg(self.__kilogram__() % other.__kilogram__())
        elif isinstance(self, ImperialWeightUnit) and isinstance(other, ImperialWeightUnit):
            return lb(self.__pound__() % other.__pound__())
        
        if is_cross_system(self, other=other):
            return kg(self.__kilogram__() % other.__kilogram__())
        
        return WeightUnit(0)  # Fallback, should not reach here.
        
    def __rmod__(self, other: 'WeightUnit') -> 'WeightUnit':
        """
        Right-hand modulo (other % self).
        
        :param other: Weight dividend.
        :type other: WeightUnit
        :return: New WeightUnit with modulo result.
        :rtype: WeightUnit
        """
        return self.__mod__(other)
    
    def __repr__(self) -> str:
        """
        Return string representation of the weight unit.
        
        :return: String in format "ClassName(value=X)".
        :rtype: str
        """
        components = [f"value={self.value}"]
        for attr in ['kilograms', 'grams', 'milligrams', 'micrograms', 
                     'pounds', 'ounces', 'grains']:
            if hasattr(self, attr):
                components.append(f"{attr}={getattr(self, attr)}")
        return f"{self.__class__.__name__}({', '.join(components)})"

    def __eq__(self, other) -> bool:
        """
        Equality comparison.
        
        :param other: Value to compare with.
        :type other: Any
        :return: True if weights are equal.
        :rtype: bool
        :raises DimensionError: If other is not a WeightUnit.
        """
        if not isinstance(other, WeightUnit):
            raise DimensionError(self, other)
        if isinstance(self, MetricWeightUnit) and isinstance(other, MetricWeightUnit):
            return self.__microgram__() == other.__microgram__() # type: ignore
        if isinstance(self, ImperialWeightUnit) and isinstance(other, ImperialWeightUnit):
            return self.__grain__() == other.__grain__() # type: ignore
        return self.__kilogram__() == other.__kilogram__() # type: ignore


class MetricWeightUnit(WeightUnit, MetricUnit):
    """
    Base class for metric system weight units (microgram through tonne).
    
    This serves as a marker class to identify metric weight units.
    All metric weight units should inherit from this class.
    """
    pass


class ImperialWeightUnit(WeightUnit, ImperialUnit):
    """
    Base class for imperial system weight units (grain through ton).
    
    This serves as a marker class to identify imperial weight units.
    All imperial weight units should inherit from this class.
    """
    pass


class Microgram(MetricWeightUnit):
    """
    Microgram (µg) - the atomic metric weight unit.
    
    This is the smallest unit in the metric weight system and serves as the
    atomic conversion base. All other metric units convert through micrograms.
    
    Conversions:
        - 1 microgram = 0.001 milligrams
        - 1 microgram = 0.000001 grams
        - 1 microgram = 1e-9 kilograms
    """
    
    def _process_value(self):
        """
        Process raw input value.
        
        For WeightUnit inputs, converts to micrograms. For numeric inputs,
        stores value directly as micrograms.
        """
        if isinstance(self.raw_value, WeightUnit):
            self.value = self.raw_value.__microgram__()
        else:
            self.value = fx(self.raw_value)

    def __microgram__(self):
        """
        Get value in micrograms.
        
        :return: Value in micrograms.
        :rtype: Fx
        """
        return self.value

    def __milligram__(self):
        """
        Convert to milligrams.
        
        :return: Value in milligrams (micrograms / 1000).
        :rtype: Fx
        """
        return self.value / 1000

    def __gram__(self):
        """
        Convert to grams.
        
        :return: Value in grams (micrograms / 1,000,000).
        :rtype: Fx
        """
        return self.value / 1_000_000

    def __kilogram__(self):
        """
        Convert to kilograms.
        
        :return: Value in kilograms (micrograms / 1,000,000,000).
        :rtype: Fx
        """
        return self.value / 1_000_000_000

    def __tonne__(self):
        """
        Convert to tonnes.
        
        :return: Value in tonnes (micrograms / 1,000,000,000,000).
        :rtype: Fx
        """
        return self.value / 1_000_000_000_000

    def __grain__(self):
        """
        Convert to grains (imperial).
        
        :return: Value in grains (1 grain = 64798.91 micrograms).
        :rtype: Fx
        """
        return self.value / Fx("64798.91")

    def __ounce__(self):
        """
        Convert to ounces (imperial).
        
        :return: Value in ounces.
        :rtype: Fx
        """
        return self.__pound__() * 16

    def __pound__(self):
        """
        Convert to pounds (imperial).
        
        :return: Value in pounds.
        :rtype: Fx
        """
        return self.__kilogram__() * Kilogram.KG_TO_LB
    
    def __ton__(self):
        """
        Convert to imperial long tons.
        
        :return: Value in long tons.
        :rtype: Fx
        """
        return self.__pound__() / 2240


class Milligram(MetricWeightUnit):
    """
    Milligram (mg) - metric weight unit.
    
    Stores whole milligrams in the `value` attribute, with any fractional
    remainder cascaded to the `micrograms` attribute for precision.
    
    Conversions:
        - 1 milligram = 1000 micrograms
        - 1 milligram = 0.001 grams
        - 1 milligram = 0.015432 grains
    """
    
    def _process_value(self):
        """
        Process raw input value.
        
        Integer inputs are stored directly. Float inputs are split into whole
        milligrams and fractional micrograms. WeightUnit inputs are converted
        via micrograms and split accordingly.
        
        :raises TypeError: If input is not a valid type.
        """
        allowed = [WeightUnit, int, float, Fx]
        if not isinstance(self.raw_value, tuple(allowed)):
            raise TypeError("Milligram must be instantiated from a WeightUnit or numeric type.")
        
        raw = self.raw_value

        if isinstance(raw, int):
            self.value = raw
            return

        if isinstance(raw, (float, Fx)):
            self.value = int(raw)
            remainder = fx(raw) - self.value
            
            rem_mcg = remainder * 1000
            if rem_mcg > 0:
                self.micrograms = rem_mcg
            return

        if isinstance(raw, WeightUnit):
            total_mcg = raw.__microgram__()
            self.value = int(total_mcg // 1000)
            rem_mcg = total_mcg % 1000
            if rem_mcg > 0:
                self.micrograms = rem_mcg

    def __microgram__(self):
        """
        Convert to micrograms.
        
        :return: Total value in micrograms (whole mg + fractional mcg).
        :rtype: Fx
        """
        total = fx(self.value) * 1000
        if hasattr(self, 'micrograms'):
            total += self.micrograms
        return total

    def __milligram__(self):
        """
        Get value in milligrams.
        
        :return: Total value in milligrams.
        :rtype: Fx
        """
        total = fx(self.value)
        if hasattr(self, 'micrograms'):
            total += self.micrograms / 1000
        return total

    def __gram__(self):
        """
        Convert to grams.
        
        :return: Value in grams.
        :rtype: Fx
        """
        return self.__milligram__() / 1000

    def __kilogram__(self):
        """
        Convert to kilograms.
        
        :return: Value in kilograms.
        :rtype: Fx
        """
        return self.__milligram__() / 1_000_000

    def __tonne__(self):
        """
        Convert to tonnes.
        
        :return: Value in tonnes.
        :rtype: Fx
        """
        return self.__milligram__() / 1_000_000_000

    def __grain__(self):
        """
        Convert to grains (imperial).
        
        :return: Value in grains (1 grain = 64.79891 mg).
        :rtype: Fx
        """
        return self.__milligram__() / Fx("64.79891")

    def __ounce__(self):
        """
        Convert to ounces (imperial).
        
        :return: Value in ounces.
        :rtype: Fx
        """
        return self.__pound__() * 16

    def __pound__(self):
        """
        Convert to pounds (imperial).
        
        :return: Value in pounds.
        :rtype: Fx
        """
        return self.__kilogram__() * Kilogram.KG_TO_LB

    def __ton__(self):
        """
        Convert to imperial long tons.
        
        :return: Value in long tons.
        :rtype: Fx
        """
        return self.__pound__() / 2240


class Gram(MetricWeightUnit):
    """
    Gram (g) - metric weight unit.
    
    Stores whole grams in the `value` attribute, with fractional remainder
    cascaded to `milligrams` and `micrograms` attributes for precision.
    
    Conversions:
        - 1 gram = 1000 milligrams
        - 1 gram = 0.001 kilograms
        - 1 gram = 15.432 grains
    """
    
    def _process_value(self):
        """
        Process raw input value.
        
        Integer inputs are stored directly. Float inputs are split into whole
        grams and cascaded fractions. WeightUnit inputs are converted via
        micrograms and split accordingly.
        
        :raises TypeError: If input is not a valid type.
        """
        allowed = [WeightUnit, int, float, Fx]
        if not isinstance(self.raw_value, tuple(allowed)):
            raise TypeError("Gram must be instantiated from a WeightUnit or numeric type.")

        raw = self.raw_value

        if isinstance(raw, int):
            self.value = raw
            return

        if isinstance(raw, (float, Fx)):
            self.value = int(raw)
            remainder = fx(raw) - self.value
            
            rem_mg = remainder * 1000
            rem_mg_int = int(snap(rem_mg))
            if rem_mg_int >= 1:
                self.milligrams = rem_mg_int
                rem_mg -= rem_mg_int
            
            rem_mcg = rem_mg * 1000
            if rem_mcg > 0:
                self.micrograms = rem_mcg
            return

        if isinstance(raw, WeightUnit):
            total_mcg = raw.__microgram__()
            self.value = int(total_mcg // 1_000_000)
            rem_mcg = total_mcg % 1_000_000
            
            if rem_mcg >= 1000:
                self.milligrams = int(rem_mcg // 1000)
                rem_mcg %= 1000
            
            if rem_mcg > 0:
                self.micrograms = rem_mcg

    def __microgram__(self):
        """
        Convert to micrograms.
        
        :return: Total value in micrograms.
        :rtype: Fx
        """
        return self.__gram__() * 1_000_000

    def __milligram__(self):
        """
        Convert to milligrams.
        
        :return: Total value in milligrams.
        :rtype: Fx
        """
        return self.__gram__() * 1000

    def __gram__(self):
        """
        Get value in grams.
        
        :return: Total value in grams (whole g + fractional mg + fractional mcg).
        :rtype: Fx
        """
        total = fx(self.value)
        if hasattr(self, 'milligrams'):
            total += fx(self.milligrams) / 1000
        if hasattr(self, 'micrograms'):
            total += fx(self.micrograms) / 1_000_000
        return total

    def __kilogram__(self):
        """
        Convert to kilograms.
        
        :return: Value in kilograms.
        :rtype: Fx
        """
        return self.__gram__() / 1000

    def __tonne__(self):
        """
        Convert to tonnes.
        
        :return: Value in tonnes.
        :rtype: Fx
        """
        return self.__gram__() / 1_000_000

    def __grain__(self):
        """
        Convert to grains (imperial).
        
        :return: Value in grains.
        :rtype: Fx
        """
        return self.__milligram__() / Fx("64.79891")

    def __ounce__(self):
        """
        Convert to ounces (imperial).
        
        :return: Value in ounces.
        :rtype: Fx
        """
        return self.__pound__() * 16

    def __pound__(self):
        """
        Convert to pounds (imperial).
        
        :return: Value in pounds.
        :rtype: Fx
        """
        return self.__kilogram__() * Kilogram.KG_TO_LB

    def __ton__(self):
        """
        Convert to imperial long tons.
        
        :return: Value in long tons.
        :rtype: Fx
        """
        return self.__pound__() / 2240


class Kilogram(MetricWeightUnit):
    """
    Kilogram (kg) - SI base unit for mass.
    
    Stores whole kilograms in the `value` attribute, with fractional remainder
    cascaded to `grams`, `milligrams`, and `micrograms` for precision.
    
    Conversions:
        - 1 kilogram = 1000 grams
        - 1 kilogram = 2.20462262185 pounds
        - 1 kilogram = 0.001 tonnes
    """
    
    KG_TO_LB = Fx("2.20462262185")
    
    def _process_value(self):
        """
        Process raw input value.
        
        Integer inputs are stored directly. Float inputs are split into whole
        kilograms and cascaded fractions. WeightUnit inputs are converted via
        micrograms and split accordingly.
        
        :raises TypeError: If input is not a valid type.
        """
        allowed = [WeightUnit, int, float, Fx]
        if not isinstance(self.raw_value, tuple(allowed)):
            raise TypeError("Kilograms can only be instantiated from another WeightUnit instance or a numeric type.")
        
        raw = self.raw_value

        if isinstance(raw, int):
            self.value = raw
            return
        
        if isinstance(raw, (float, Fx)):
            self.value = int(raw)
            remainder = fx(raw) - self.value
            
            rem_g = remainder * 1000
            rem_g_int = int(snap(rem_g))
            if rem_g_int >= 1:
                self.grams = rem_g_int
                rem_g -= rem_g_int
            
            rem_mg = rem_g * 1000
            rem_mg_int = int(snap(rem_mg))
            if rem_mg_int >= 1:
                self.milligrams = rem_mg_int
                rem_mg -= rem_mg_int
            
            rem_mcg = rem_mg * 1000
            if rem_mcg > 0:
                self.micrograms = rem_mcg
            return
                    
        if isinstance(raw, WeightUnit):
            total_mcg = raw.__microgram__()
            self.value = int(total_mcg // 1_000_000_000)
            remaining_mcg = total_mcg % 1_000_000_000
            
            if remaining_mcg >= 1_000_000:
                self.grams = int(remaining_mcg // 1_000_000)
                remaining_mcg %= 1_000_000
            
            if remaining_mcg >= 1_000:
                self.milligrams = int(remaining_mcg // 1_000)
                remaining_mcg %= 1_000
            
            if remaining_mcg > 0:
                self.micrograms = remaining_mcg

    def __microgram__(self):
        """
        Convert to micrograms.
        
        :return: Total value in micrograms.
        :rtype: Fx
        """
        return self.__kilogram__() * 1_000_000_000

    def __milligram__(self):
        """
        Convert to milligrams.
        
        :return: Total value in milligrams.
        :rtype: Fx
        """
        return self.__kilogram__() * 1_000_000

    def __gram__(self):
        """
        Convert to grams.
        
        :return: Total value in grams.
        :rtype: Fx
        """
        return self.__kilogram__() * 1000

    def __kilogram__(self):
        """
        Get value in kilograms.
        
        :return: Total value in kilograms (whole kg + fractional components).
        :rtype: Fx
        """
        total_kg = fx(self.value)
        if hasattr(self, 'grams'):
            total_kg += fx(self.grams) / 1000
        if hasattr(self, 'milligrams'):
            total_kg += fx(self.milligrams) / 1_000_000
        if hasattr(self, 'micrograms'):
            total_kg += fx(self.micrograms) / 1_000_000_000
        return total_kg
    
    def __tonne__(self):
        """
        Convert to tonnes.
        
        :return: Value in tonnes.
        :rtype: Fx
        """
        return self.__kilogram__() / 1000
    
    def __pound__(self):
        """
        Convert to pounds (imperial).
        
        :return: Value in pounds.
        :rtype: Fx
        """
        return self.__kilogram__() * self.KG_TO_LB

    def __ounce__(self):
        """
        Convert to ounces (imperial).
        
        :return: Value in ounces.
        :rtype: Fx
        """
        return self.__pound__() * 16

    def __grain__(self):
        """
        Convert to grains (imperial).
        
        :return: Value in grains.
        :rtype: Fx
        """
        return self.__milligram__() / Fx("64.79891")

    def __ton__(self):
        """
        Convert to imperial long tons.
        
        :return: Value in long tons.
        :rtype: Fx
        """
        return self.__pound__() / 2240


class Tonne(MetricWeightUnit):
    """
    Tonne (metric ton) - large metric weight unit.
    
    Stores whole tonnes in the `value` attribute, with fractional remainder
    cascaded to smaller units for precision.
    
    Conversions:
        - 1 tonne = 1000 kilograms
        - 1 tonne = 1,000,000 grams
        - 1 tonne = 2204.62 pounds
    """
    
    def _process_value(self):
        """
        Process raw input value.
        
        Integer inputs are stored directly. Float inputs are split into whole
        tonnes and cascaded fractions. WeightUnit inputs are converted via
        kilograms and split accordingly.
        
        :raises TypeError: If input is not a valid type.
        """
        allowed = [WeightUnit, int, float, Fx]
        if not isinstance(self.raw_value, tuple(allowed)):
            raise TypeError("Tonne must be instantiated from a WeightUnit or numeric type.")

        raw = self.raw_value

        if isinstance(raw, int):
            self.value = raw
            return

        if isinstance(raw, (float, Fx)):
            self.value = int(raw)
            remainder = fx(raw) - self.value
            
            rem_kg = remainder * 1000
            rem_kg_int = int(snap(rem_kg))
            if rem_kg_int >= 1:
                self.kilograms = rem_kg_int
                rem_kg -= rem_kg_int
            
            rem_g = rem_kg * 1000
            rem_g_int = int(snap(rem_g))
            if rem_g_int >= 1:
                self.grams = rem_g_int
                rem_g -= rem_g_int
            
            rem_mg = rem_g * 1000
            rem_mg_int = int(snap(rem_mg))
            if rem_mg_int >= 1:
                self.milligrams = rem_mg_int
                rem_mg -= rem_mg_int
            
            rem_mcg = rem_mg * 1000
            if rem_mcg > 0:
                self.micrograms = rem_mcg

    def __tonne__(self):
        """
        Get value in tonnes.
        
        :return: Total value in tonnes (whole tonnes + fractional components).
        :rtype: Fx
        """
        total = fx(self.value)
        if hasattr(self, 'kilograms'):
            total += fx(self.kilograms) / 1000
        if hasattr(self, 'grams'):
            total += fx(self.grams) / 1_000_000
        if hasattr(self, 'milligrams'):
            total += fx(self.milligrams) / 1_000_000_000
        if hasattr(self, 'micrograms'):
            total += fx(self.micrograms) / 1_000_000_000_000
        return total

    def __kilogram__(self):
        """
        Convert to kilograms.
        
        :return: Total value in kilograms.
        :rtype: Fx
        """
        return self.__tonne__() * 1000

    def __gram__(self):
        """
        Convert to grams.
        
        :return: Total value in grams.
        :rtype: Fx
        """
        return self.__tonne__() * 1_000_000

    def __milligram__(self):
        """
        Convert to milligrams.
        
        :return: Total value in milligrams.
        :rtype: Fx
        """
        return self.__tonne__() * 1_000_000_000
    
    def __microgram__(self):
        """
        Convert to micrograms.
        
        :return: Total value in micrograms.
        :rtype: Fx
        """
        return self.__tonne__() * 1_000_000_000_000

    def __pound__(self):
        """
        Convert to pounds (imperial).
        
        :return: Value in pounds.
        :rtype: Fx
        """
        return self.__kilogram__() * Kilogram.KG_TO_LB
    
    def __ounce__(self):
        """
        Convert to ounces (imperial).
        
        :return: Value in ounces.
        :rtype: Fx
        """
        return self.__pound__() * 16

    def __grain__(self):
        """
        Convert to grains (imperial).
        
        :return: Value in grains.
        :rtype: Fx
        """
        return self.__milligram__() / Fx("64.79891")
    
    def __ton__(self):
        """
        Convert to imperial long tons.
        
        :return: Value in long tons.
        :rtype: Fx
        """
        return self.__pound__() / 2240


class Grain(ImperialWeightUnit):
    """
    Grain (gr) - the atomic imperial weight unit.
    
    This is the smallest unit in the imperial weight system and serves as the
    atomic conversion base. All other imperial units convert through grains.
    
    Conversions:
        - 1 pound = 7000 grains
        - 1 ounce = 437.5 grains
        - 1 grain = 64.79891 milligrams
    """
    
    def _process_value(self):
        """
        Process raw input value.
        
        For WeightUnit inputs, converts to grains. For numeric inputs,
        stores value directly as grains.
        
        :raises TypeError: If input is not a valid type.
        """
        allowed = [WeightUnit, int, float, Fx]
        if not isinstance(self.raw_value, tuple(allowed)):
            raise TypeError("Grain inputs must be valid.")

        if isinstance(self.raw_value, WeightUnit):
            self.value = self.raw_value.__grain__()
        else:
            self.value = fx(self.raw_value)

    def __grain__(self):
        """
        Get value in grains.
        
        :return: Value in grains.
        :rtype: Fx
        """
        return self.value

    def __ounce__(self):
        """
        Convert to ounces.
        
        :return: Value in ounces (grains / 437.5).
        :rtype: Fx
        """
        return self.value / 437.5

    def __pound__(self):
        """
        Convert to pounds.
        
        :return: Value in pounds (grains / 7000).
        :rtype: Fx
        """
        return self.value / 7000

    def __ton__(self):
        """
        Convert to imperial long tons.
        
        :return: Value in long tons.
        :rtype: Fx
        """
        return self.__pound__() / 2240

    def __milligram__(self):
        """
        Convert to milligrams (metric).
        
        :return: Value in milligrams (1 grain = 64.79891 mg).
        :rtype: Fx
        """
        return self.value * Fx("64.79891")

    def __microgram__(self):
        """
        Convert to micrograms (metric).
        
        :return: Value in micrograms.
        :rtype: Fx
        """
        return self.__milligram__() * 1000

    def __gram__(self):
        """
        Convert to grams (metric).
        
        :return: Value in grams.
        :rtype: Fx
        """
        return self.__milligram__() / 1000

    def __kilogram__(self):
        """
        Convert to kilograms (metric).
        
        :return: Value in kilograms.
        :rtype: Fx
        """
        return self.__milligram__() / 1_000_000
        
    def __tonne__(self):
        """
        Convert to tonnes (metric).
        
        :return: Value in tonnes.
        :rtype: Fx
        """
        return self.__kilogram__() / 1000


class Ounce(ImperialWeightUnit):
    """
    Ounce (oz) - imperial weight unit.
    
    Stores whole ounces in the `value` attribute, with fractional remainder
    in the `grains` attribute for precision.
    
    Conversions:
        - 1 ounce = 437.5 grains
        - 1 ounce = 1/16 pound
        - 1 ounce = 28.3495 grams
    """
    
    def _process_value(self):
        """
        Process raw input value.
        
        Integer inputs are stored directly. Float inputs are split into whole
        ounces and fractional grains. WeightUnit inputs are converted via
        grains and split accordingly.
        
        :raises TypeError: If input is not a valid type.
        """
        allowed = [WeightUnit, int, float, Fx]
        if not isinstance(self.raw_value, tuple(allowed)):
            raise TypeError("Ounce inputs must be valid.")

        raw = self.raw_value

        if isinstance(raw, int):
            self.value = raw
            return

        if isinstance(raw, (float, Fx)):
            self.value = int(raw)
            remainder = fx(raw) - self.value
            
            rem_gr = remainder * 437.5
            if rem_gr > 0:
                self.grains = rem_gr
            return

        if isinstance(raw, WeightUnit):
            total_gr = raw.__grain__()
            self.value = int(total_gr // 437.5)
            rem_gr = total_gr % 437.5
            if rem_gr > 0:
                self.grains = rem_gr

    def __ounce__(self):
        """
        Get value in ounces.
        
        :return: Total value in ounces (whole oz + fractional grains).
        :rtype: Fx
        """
        total = fx(self.value)
        if hasattr(self, 'grains'):
            total += self.grains / 437.5
        return total

    def __grain__(self):
        """
        Convert to grains.
        
        :return: Total value in grains.
        :rtype: Fx
        """
        total = fx(self.value) * 437.5
        if hasattr(self, 'grains'):
            total += self.grains
        return total
    
    def __pound__(self):
        """
        Convert to pounds.
        
        :return: Value in pounds.
        :rtype: Fx
        """
        return self.__ounce__() / 16
    
    def __ton__(self):
        """
        Convert to imperial long tons.
        
        :return: Value in long tons.
        :rtype: Fx
        """
        return self.__pound__() / 2240

    def __kilogram__(self):
        """
        Convert to kilograms (metric).
        
        :return: Value in kilograms.
        :rtype: Fx
        """
        return (self.__ounce__() / 16) * Pound.LB_TO_KG
    
    def __gram__(self):
        """
        Convert to grams (metric).
        
        :return: Value in grams.
        :rtype: Fx
        """
        return self.__kilogram__() * 1000

    def __milligram__(self):
        """
        Convert to milligrams (metric).
        
        :return: Value in milligrams.
        :rtype: Fx
        """
        return self.__kilogram__() * 1_000_000
    
    def __microgram__(self):
        """
        Convert to micrograms (metric).
        
        :return: Value in micrograms.
        :rtype: Fx
        """
        return self.__kilogram__() * 1_000_000_000

    def __tonne__(self):
        """
        Convert to tonnes (metric).
        
        :return: Value in tonnes.
        :rtype: Fx
        """
        return self.__kilogram__() / 1000


class Pound(ImperialWeightUnit):
    """
    Pound (lb) - imperial base unit for mass.
    
    Stores whole pounds in the `value` attribute, with fractional remainder
    cascaded to `ounces` and `grains` for precision.
    
    Conversions:
        - 1 pound = 16 ounces
        - 1 pound = 7000 grains
        - 1 pound = 0.45359237 kilograms
    """
    
    LB_TO_KG = Fx("0.45359237")

    def _process_value(self):
        """
        Process raw input value.
        
        Integer inputs are stored directly. Float inputs are split into whole
        pounds and cascaded fractions. WeightUnit inputs are converted via
        grains and split accordingly.
        
        :raises TypeError: If input is not a valid type.
        """
        allowed = [WeightUnit, int, float, Fx]
        if not isinstance(self.raw_value, tuple(allowed)):
            raise TypeError("Pound must be instantiated from a WeightUnit or numeric type.")
        
        raw = self.raw_value

        if isinstance(raw, int):
            self.value = raw
            return

        if isinstance(raw, (float, Fx)):
            self.value = int(raw)
            remainder = fx(raw) - self.value
            
            rem_oz = remainder * 16
            rem_oz_int = int(snap(rem_oz))
            if rem_oz_int >= 1:
                self.ounces = rem_oz_int
                rem_oz -= rem_oz_int
            
            rem_gr = rem_oz * 437.5
            if rem_gr > 0:
                self.grains = rem_gr
            return

        if isinstance(raw, WeightUnit):
            total_gr = raw.__grain__()
            self.value = int(total_gr // 7000)
            rem_gr = total_gr % 7000
            
            if rem_gr >= 437.5:
                self.ounces = int(rem_gr // 437.5)
                rem_gr %= 437.5
            
            if rem_gr > 0:
                self.grains = rem_gr

    def __pound__(self):
        """
        Get value in pounds.
        
        :return: Total value in pounds (whole lb + fractional components).
        :rtype: Fx
        """
        total = fx(self.value)
        if hasattr(self, 'ounces'):
            total += fx(self.ounces) / 16
        if hasattr(self, 'grains'):
            total += fx(self.grains) / 7000
        return total

    def __grain__(self):
        """
        Convert to grains.
        
        :return: Total value in grains.
        :rtype: Fx
        """
        return self.__pound__() * 7000

    def __ounce__(self):
        """
        Convert to ounces.
        
        :return: Total value in ounces.
        :rtype: Fx
        """
        return self.__pound__() * 16

    def __ton__(self):
        """
        Convert to imperial long tons.
        
        :return: Value in long tons.
        :rtype: Fx
        """
        return self.__pound__() / 2240

    def __kilogram__(self):
        """
        Convert to kilograms (metric).
        
        :return: Value in kilograms.
        :rtype: Fx
        """
        return self.__pound__() * self.LB_TO_KG

    def __gram__(self):
        """
        Convert to grams (metric).
        
        :return: Value in grams.
        :rtype: Fx
        """
        return self.__kilogram__() * 1000

    def __milligram__(self):
        """
        Convert to milligrams (metric).
        
        :return: Value in milligrams.
        :rtype: Fx
        """
        return self.__kilogram__() * 1_000_000
    
    def __microgram__(self):
        """
        Convert to micrograms (metric).
        
        :return: Value in micrograms.
        :rtype: Fx
        """
        return self.__kilogram__() * 1_000_000_000

    def __tonne__(self):
        """
        Convert to tonnes (metric).
        
        :return: Value in tonnes.
        :rtype: Fx
        """
        return self.__kilogram__() / 1000


class Ton(ImperialWeightUnit):
    """
    Imperial Long Ton - large imperial weight unit.
    
    Stores whole tons in the `value` attribute, with fractional remainder
    cascaded to smaller units for precision.
    
    Conversions:
        - 1 long ton = 2240 pounds
        - 1 long ton = 35,840 ounces
        - 1 long ton = 1016.0469088 kilograms
    
    Note: This is the imperial long ton, not the US short ton (2000 lbs).
    """

    def _process_value(self):
        """
        Process raw input value.
        
        Integer inputs are stored directly. Float inputs are split into whole
        tons and cascaded fractions. WeightUnit inputs are converted via
        grains and split accordingly.
        
        :raises TypeError: If input is not a valid type.
        """
        allowed = [WeightUnit, int, float, Fx]
        if not isinstance(self.raw_value, tuple(allowed)):
            raise TypeError("Ton must be instantiated from a WeightUnit or numeric type.")
        
        raw = self.raw_value

        if isinstance(raw, int):
            self.value = raw
            return

        if isinstance(raw, (float, Fx)):
            self.value = int(raw)
            remainder = fx(raw) - self.value
            
            rem_lbs = remainder * 2240
            rem_lbs_int = int(snap(rem_lbs))
            if rem_lbs_int >= 1:
                self.pounds = rem_lbs_int
                rem_lbs -= rem_lbs_int
            
            rem_oz = rem_lbs * 16
            rem_oz_int = int(snap(rem_oz))
            if rem_oz_int >= 1:
                self.ounces = rem_oz_int
                rem_oz -= rem_oz_int
            
            rem_gr = rem_oz * 437.5
            if rem_gr > 0:
                self.grains = rem_gr
            return

        if isinstance(raw, WeightUnit):
            total_gr = raw.__grain__()
            TON_IN_GRAINS = 15_680_000
            
            self.value = int(total_gr // TON_IN_GRAINS)
            rem_gr = total_gr % TON_IN_GRAINS
            
            if rem_gr >= 7000:
                self.pounds = int(rem_gr // 7000)
                rem_gr %= 7000
            
            if rem_gr >= 437.5:
                self.ounces = int(rem_gr // 437.5)
                rem_gr %= 437.5
                
            if rem_gr > 0:
                self.grains = rem_gr

    def __ton__(self):
        """
        Get value in long tons.
        
        :return: Total value in long tons (whole tons + fractional components).
        :rtype: Fx
        """
        total = fx(self.value)
        if hasattr(self, 'pounds'):
            total += fx(self.pounds) / 2240
        if hasattr(self, 'ounces'):
            total += (fx(self.ounces) / 16) / 2240
        if hasattr(self, 'grains'):
            total += (fx(self.grains) / 7000) / 2240
        return total

    def __pound__(self):
        """
        Convert to pounds.
        
        :return: Total value in pounds.
        :rtype: Fx
        """
        return self.__ton__() * 2240

    def __ounce__(self):
        """
        Convert to ounces.
        
        :return: Total value in ounces.
        :rtype: Fx
        """
        return self.__ton__() * 35840

    def __grain__(self):
        """
        Convert to grains.
        
        :return: Total value in grains.
        :rtype: Fx
        """
        return self.__ton__() * 15_680_000

    def __kilogram__(self):
        """
        Convert to kilograms (metric).
        
        :return: Value in kilograms.
        :rtype: Fx
        """
        return self.__pound__() * Pound.LB_TO_KG

    def __gram__(self):
        """
        Convert to grams (metric).
        
        :return: Value in grams.
        :rtype: Fx
        """
        return self.__kilogram__() * 1000

    def __milligram__(self):
        """
        Convert to milligrams (metric).
        
        :return: Value in milligrams.
        :rtype: Fx
        """
        return self.__kilogram__() * 1_000_000
    
    def __microgram__(self):
        """
        Convert to micrograms (metric).
        
        :return: Value in micrograms.
        :rtype: Fx
        """
        return self.__kilogram__() * 1_000_000_000

    def __tonne__(self):
        """
        Convert to tonnes (metric).
        
        :return: Value in tonnes.
        :rtype: Fx
        """
        return self.__kilogram__() / 1000


NumericInput: TypeAlias = Union[int, float, Fx]

def kg(value: 'WeightUnit | NumericInput') -> Kilogram:
    """
    Create a Kilogram instance from a value or another weight unit.
    
    :param value: Numeric value in kilograms, or another WeightUnit to convert.
    :type value: WeightUnit | NumericInput
    :return: Kilogram instance.
    :rtype: Kilogram
    """
    if isinstance(value, WeightUnit):
        return Kilogram(value.__kilogram__())
    else:
        return Kilogram(value)

def gram(value: 'WeightUnit | NumericInput') -> Gram:
    """
    Create a Gram instance from a value or another weight unit.
    
    :param value: Numeric value in grams, or another WeightUnit to convert.
    :type value: WeightUnit | NumericInput
    :return: Gram instance.
    :rtype: Gram
    """
    if isinstance(value, WeightUnit):
        return Gram(value.__gram__())
    else:
        return Gram(value)

def mg(value: 'WeightUnit | NumericInput') -> Milligram:
    """
    Create a Milligram instance from a value or another weight unit.
    
    :param value: Numeric value in milligrams, or another WeightUnit to convert.
    :type value: WeightUnit | NumericInput
    :return: Milligram instance.
    :rtype: Milligram
    """
    if isinstance(value, WeightUnit):
        return Milligram(value.__milligram__())
    else:
        return Milligram(value)

def mcg(value: 'WeightUnit | NumericInput') -> Microgram:
    """
    Create a Microgram instance from a value or another weight unit.
    
    :param value: Numeric value in micrograms, or another WeightUnit to convert.
    :type value: WeightUnit | NumericInput
    :return: Microgram instance.
    :rtype: Microgram
    """
    if isinstance(value, WeightUnit):
        return Microgram(value.__microgram__())
    else:
        return Microgram(value)

def tonne(value: 'WeightUnit | NumericInput') -> Tonne:
    """
    Create a Tonne instance from a value or another weight unit.
    
    :param value: Numeric value in tonnes, or another WeightUnit to convert.
    :type value: WeightUnit | NumericInput
    :return: Tonne instance.
    :rtype: Tonne
    """
    if isinstance(value, WeightUnit):
        return Tonne(value.__tonne__())
    else:
        return Tonne(value)

def lb(value: 'WeightUnit | NumericInput') -> Pound:
    """
    Create a Pound instance from a value or another weight unit.
    
    :param value: Numeric value in pounds, or another WeightUnit to convert.
    :type value: WeightUnit | NumericInput
    :return: Pound instance.
    :rtype: Pound
    """
    if isinstance(value, WeightUnit):
        return Pound(value.__pound__())
    else:
        return Pound(value)

def oz(value: 'WeightUnit | NumericInput') -> Ounce:
    """
    Create an Ounce instance from a value or another weight unit.
    
    :param value: Numeric value in ounces, or another WeightUnit to convert.
    :type value: WeightUnit | NumericInput
    :return: Ounce instance.
    :rtype: Ounce
    """
    if isinstance(value, WeightUnit):
        return Ounce(value.__ounce__())
    else:
        return Ounce(value)

def ton(value: 'WeightUnit | NumericInput') -> Ton:
    """
    Create a Ton instance from a value or another weight unit.
    
    :param value: Numeric value in long tons, or another WeightUnit to convert.
    :type value: WeightUnit | NumericInput
    :return: Ton instance.
    :rtype: Ton
    """
    if isinstance(value, WeightUnit):
        return Ton(value.__ton__())
    else:
        return Ton(value)

def grain(value: 'WeightUnit | NumericInput') -> Grain:
    """
    Create a Grain instance from a value or another weight unit.
    
    :param value: Numeric value in grains, or another WeightUnit to convert.
    :type value: WeightUnit | NumericInput
    :return: Grain instance.
    :rtype: Grain
    """
    if isinstance(value, WeightUnit):
        return Grain(value.__grain__())
    else:
        return Grain(value)