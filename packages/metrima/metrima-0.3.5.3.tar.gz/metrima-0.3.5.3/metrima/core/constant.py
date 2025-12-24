"""
Constant module providing immutable value container functionality.

This module contains the Constant class which creates immutable containers
for values. Once initialized, the value cannot be modified or deleted.
"""

from metrima.utils.errors import ConstantError

class Constant:
    """
    An immutable container for a single constant value.
    
    Attempts to change any attribute after initialization will fail.
    
    :param value: The constant value to store.
    :type value: int
    """
    def __init__(self, value: int) -> None:
        object.__setattr__(self, 'value', value)

    def __setattr__(self, name, value) -> None:
        """
        Prevent modification of any attribute after initialization.
        
        :param name: Attribute name.
        :type name: str
        :param value: Value to set.
        :type value: Any
        :raises ConstantError: Always, since Constant objects are immutable.
        """
        raise ConstantError()

    def __delattr__(self, name) -> None:
        """
        Prevent deletion of attributes from Constant objects.
        
        :param name: Attribute name.
        :type name: str
        :raises ConstantError: Always, since Constant objects are immutable.
        """
        raise ConstantError()

    def __repr__(self) -> str:
        """
        Return official string representation of the Constant object.
        
        :return: String representation suitable for reproduction.
        :rtype: str
        """
        return f"Constant({self.value!r})" # type: ignore

    def __str__(self) -> str:
        """
        Return informal string representation of the Constant object.
        
        :return: String representation of the stored value.
        :rtype: str
        """
        return str(self.value) # type: ignore