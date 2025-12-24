"""
Temporary module providing single-use value wrapper functionality.

This module contains the Temporary class which wraps a value that can only
be accessed once. After the first attribute access, the wrapped value is
cleared and cannot be accessed again.
"""

from typing import Any

class Temporary:
    """
    A wrapper class that allows only one access to the wrapped value.
    
    Once any attribute is accessed, the wrapped value is cleared and cannot
    be accessed again. This is useful for ensuring single-use values.
    
    :param value: The value to wrap temporarily.
    :type value: Any
    """
    def __init__(self, value: Any):
        super().__setattr__("_Temporary__value", value)

    def __getattribute__(self, name: str) -> Any:
        """
        Get an attribute from the wrapped value.
        
        On first access, clears the wrapped value. Subsequent accesses
        raise AttributeError.
        
        :param name: The name of the attribute to access.
        :type name: str
        :return: The attribute value from the wrapped object, or the
                 wrapped value itself if name is "value".
        :rtype: Any
        :raises AttributeError: If the wrapped value has already been
                                accessed or doesn't exist.
        """
        try:
            value = super().__getattribute__("_Temporary__value")
        except AttributeError:
            raise AttributeError("Wrapped object is gone (accessed Temporary value once)")

        if value is None:
            raise AttributeError("Wrapped object is gone (accessed Temporary value once)")

        super().__setattr__("_Temporary__value", None)

        if name == "value":
            return value
        else:
            return getattr(value, name)

    def __setattr__(self, name, value):
        """
        Prevent modification of Temporary objects.
        
        :param name: Attribute name.
        :type name: str
        :param value: Value to set.
        :type value: Any
        :raises AttributeError: Always, since Temporary objects are immutable.
        """
        raise AttributeError("Cannot modify a Temporary object")

    def __delattr__(self, name):
        """
        Prevent deletion of attributes from Temporary objects.
        
        :param name: Attribute name.
        :type name: str
        :raises AttributeError: Always, since Temporary objects are immutable.
        """
        raise AttributeError("Cannot delete attributes of a Temporary object")

    def __str__(self):
        """
        Return string representation of the wrapped value.
        
        :return: String representation of the value.
        :rtype: str
        """
        return f"{self.value}"

def temp(value: Any) -> Temporary:
    """
    Create a Temporary wrapper for a value.
    
    :param value: The value to wrap.
    :type value: Any
    :return: A Temporary instance containing the value.
    :rtype: Temporary
    """
    return Temporary(value)