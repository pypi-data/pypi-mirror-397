"""
Utility function for checking if a value "exists" in a meaningful way.

This module provides a function to determine if a value is considered
"truthy" according to specific rules that treat various false-like
values as non-existent.
"""

def exists(value) -> bool:
    """
    Check if a value exists (is truthy according to specific rules).
    
    Returns False for values that are considered "empty" or "false-like":
    - None
    - False
    - Empty containers: [], "", {}, ()
    - Zero values: 0.0, 0
    
    All other values return True.
    
    :param value: The value to check for existence.
    :type value: Any
    :return: True if the value exists, False otherwise.
    :rtype: bool
    """
    if value is None:
        return False
    if value is False:
        return False
    if value in ([], "", {}, ()):
        return False
    if value in (0.0, 0):
        return False
    else:
        return True