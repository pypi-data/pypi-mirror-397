"""
Utility functions and base classes for unit conversions and operations.

This module provides the base classes for metric and imperial units,
along with utility functions for value downgrading and system detection.
"""

from ..core.fixed import Fx
from metrima.lib import is_whole
from typing import List, Tuple, Optional

def downgrade_float_fx(value: float, chain: List[Tuple[int, str]]) -> Tuple[int, Optional[Tuple[str, Fx]]]:
    """
    Downgrades a float through a chain of conversion factors until we get a whole number.
    
    :param value: Original float value.
    :type value: float
    :param chain: List of (factor, unit_name) tuples, e.g., [(60, "minutes"), (60, "seconds"), (1000, "milliseconds")].
    :type chain: List[Tuple[int, str]]
    :return: (whole_value: int, leftover: Optional[Tuple[str, Fx]]).
    :rtype: Tuple[int, Optional[Tuple[str, Fx]]]
    """
    current_val = Fx(value)
    
    for i, (factor, unit_name) in enumerate(chain):
        current_val *= Fx(factor)
        
        if is_whole(current_val):
            remaining_chain = chain[i+1:]
            for next_factor, _ in remaining_chain:
                current_val *= Fx(next_factor)
            return int(current_val), None
            
    return int(current_val), (unit_name, current_val)


class MetricUnit:
    """
    Base class for all metric system units.
    
    This serves as a marker class to identify units belonging to the metric
    measurement system. All metric units should inherit from this class.
    """
    pass

class ImperialUnit:
    """
    Base class for all imperial system units.
    
    This serves as a marker class to identify units belonging to the imperial
    measurement system. All imperial units should inherit from this class.
    """
    pass