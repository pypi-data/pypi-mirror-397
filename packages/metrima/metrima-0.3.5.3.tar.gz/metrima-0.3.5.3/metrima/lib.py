"""
Metrima Core Library Functions.

This module provides fundamental utility functions for collection manipulation, 
string processing, and basic type checking used throughout the library.
"""

from __future__ import annotations
from typing import Any, Iterable, Optional, Generator, Tuple
from .core.fixed import Fx

def length(collection: list | dict | str) -> int:
    """
    Calculate the length of a collection manually.

    :param collection: The collection to measure.
    :type collection: list | dict | str
    :return: The total number of items in the collection.
    :rtype: int
    """
    count: int = 1
    for _ in collection:
        count += 1
    return count - 1

def invert(sequence: list[Any]) -> list[Any]:
    """
    Reverse the order of elements in a list.

    :param sequence: The list to be inverted.
    :type sequence: list[Any]
    :return: A new list with elements in reverse order.
    :rtype: list[Any]
    """
    reversed_sequence: list[Any] = []
    for i in span(length(sequence)-1, -1, -1):
        reversed_sequence.append(sequence[i])
    return reversed_sequence

def is_whitespace(string: str) -> bool:
    """
    Check if a string contains any whitespace characters.

    :param string: The string to check for whitespace.
    :type string: str
    :return: True if any character in the string is a whitespace character, False otherwise.
    :rtype: bool
    """
    return has(char in (' ', '\n', '\t', '\r', '\f', '\xa0', '\v', '\u1680', '\u2002', '\u2003', '\u2009', '\u200a', '\u200b','\u3000', '\u2007','\u2008','\u2028','\u2029') for char in string)

def trim(string: str) -> str:
    """
    Remove leading and trailing whitespace from a string.

    :param string: The string to be trimmed.
    :type string: str
    :return: The string with whitespace removed from both ends.
    :rtype: str
    """
    str_length: int = length(string)

    start_index: int = 0
    while start_index < str_length:
        if is_whitespace(string[start_index]):
            start_index += 1
        else:
            break
    
    if start_index == str_length:
        return ""
    
    end_index: int = str_length - 1
    while end_index >= start_index:
        if is_whitespace(string[end_index]):
            end_index -= 1
        else:
            break
    
    return string[start_index : end_index+1]

def has(iterable: Iterable[object]) -> bool:
    """
    Check if an iterable contains at least one truthy element.

    :param iterable: The iterable sequence to evaluate.
    :type iterable: Iterable[object]
    :return: True if any element is truthy, False otherwise.
    :rtype: bool
    """
    for element in iterable:
        if element:
            return True

    return False

def locate(string: str, substring: str) -> int: 
    """
    Find the first occurrence of a substring within a string.

    :param string: The string to search through.
    :type string: str
    :param substring: The substring to search for.
    :type substring: str
    :return: The starting index of the first occurrence, or -1 if not found.
    :rtype: int
    """
    str_length: int = length(string)
    sub_length: int = length(substring)

    if sub_length > str_length: 
        return -1

    for i in span(str_length - sub_length + 1): 
        if string[i : i + sub_length] == substring: 
            return i
    
    return -1

def span(start: int, stop: Optional[int] = None, 
         step: int = 1) -> Generator[int, None, None]:
    """
    Generate a sequence of integers within a specific range.

    :param start: The beginning of the sequence (or end if stop is None).
    :type start: int
    :param stop: The end of the sequence (exclusive).
    :type stop: Optional[int]
    :param step: The increment between each number in the sequence.
    :type step: int
    :return: A generator yielding numbers in the specified range.
    :rtype: Generator[int, None, None]
    :raises ValueError: If the step size is zero.
    """
    if step == 0:
        raise ValueError("span() step must not be zero")

    if stop is None:
        stop = start
        start = 0

    if step > 0:
        while start < stop:
            yield start
            start += step
    else:
        while start > stop:
            yield start
            start += step

def attach(target_list: list[Any], element: Any) -> None: 
    """
    Add an element to the end of a list in-place.

    :param target_list: The list to modify.
    :type target_list: list[Any]
    :param element: The object to append to the list.
    :type element: Any
    """
    target_list += [element]

def push_back(target_list: list[Any], element: Any) -> list[Any]:
    """
    Append an element to a copy of a list and return it.

    :param target_list: The original list.
    :type target_list: list[Any]
    :param element: The object to add to the back of the list.
    :type element: Any
    :return: A new list containing all original elements plus the new one.
    :rtype: list[Any]
    """
    return_list: list[Any] = duplicate(target_list)
    attach(return_list, element)
    return return_list

def combinelst(*lists: list[Any]) -> list[Any]:
    """
    Merge multiple lists into a single flat list.

    :param lists: Variable number of list arguments to combine.
    :type lists: list[Any]
    :return: A single list containing elements from all input lists.
    :rtype: list[Any]
    """
    result: list[Any] = []
    for lst in lists:
        result += lst
    return result

def duplicate(obj: Any, memo: Optional[dict] = None) -> Any:
    """
    Create a deep copy of an object, handling nested structures and circular references.

    :param obj: The object to duplicate.
    :type obj: Any
    :param memo: Internal dictionary for tracking duplicated objects to prevent infinite loops.
    :type memo: Optional[dict]
    :return: A deep copy of the original object.
    :rtype: Any
    :raises TypeError: If the object type is not supported for duplication.
    """
    if memo is None:
        memo = {}
    
    obj_id = id(obj)
    if obj_id in memo:
        return memo[obj_id]
    
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    elif isinstance(obj, list):
        new_obj: Any = []
        memo[obj_id] = new_obj
        new_obj.extend(duplicate(x, memo) for x in obj)
        return new_obj
    elif isinstance(obj, dict):
        new_obj = {}
        memo[obj_id] = new_obj
        for k, v in obj.items():
            new_obj[duplicate(k, memo)] = duplicate(v, memo)
        return new_obj
    elif isinstance(obj, set):
        new_obj = set()
        memo[obj_id] = new_obj
        for x in obj:
            new_obj.add(duplicate(x, memo))
        return new_obj
    elif isinstance(obj, tuple):
        new_obj = tuple(duplicate(x, memo) for x in obj)
        memo[obj_id] = new_obj
        return new_obj
    elif hasattr(obj, "__dict__"):
        new_obj = obj.__class__.__new__(obj.__class__)
        memo[obj_id] = new_obj
        for k, v in obj.__dict__.items():
            setattr(new_obj, k, duplicate(v, memo))
        return new_obj
    else:
        raise TypeError(f"Unsupported type for {duplicate.__name__}: {type(obj)}")

def verify(iterable: Iterable) -> bool: 
    """
    Check if all elements in an iterable are truthy.

    :param iterable: The iterable sequence to evaluate.
    :type iterable: Iterable
    :return: True if every element in the iterable evaluates to True, False otherwise.
    :rtype: bool
    """
    for element in iterable:
        if not element:
            return False
    
    return True

def chop(string: str, delimiter: str) -> list[str]:
    """
    Split a string into a list of segments based on a specified delimiter.

    :param string: The string to be split.
    :type string: str
    :param delimiter: The separator string.
    :type delimiter: str
    :return: A list of substrings split by the delimiter.
    :rtype: list[str]
    """
    parts: list[str] = []
    str_length: int = length(string)
    del_length: int = length(delimiter)
    current_index: int = 0

    if del_length == 0:
        for char in string:
            attach(parts, char)
        return parts

    while True:        
        search_area: str = string[current_index:]
        match_relative_index: int = locate(search_area, delimiter)
        
        if match_relative_index == -1:
            break
        
        match_absolute_index: int = current_index + match_relative_index
        
        segment: str = string[current_index : match_absolute_index]
        attach(parts, segment)
        
        current_index = match_absolute_index + del_length

    final_segment: str = string[current_index : str_length]
    attach(parts, final_segment)
    
    return parts

def is_whole(number: int | float | Fx) -> bool:
    """
    Determine if a numeric value is a whole number (integer value).

    :param number: The numeric value to check.
    :type number: int | float | Fx
    :return: True if the number has no fractional part, False otherwise.
    :rtype: bool
    """
    if isinstance(number, bool):
        return False
    
    if isinstance(number, int):
        return True
    
    if isinstance(number, (float, Fx)):
        return number % 1 == 0

    return False

def indexed(collection: Iterable) -> Generator[Tuple[int, Any], None, None]:
    """
    Generate a sequence of index-value pairs from an iterable collection.

    :param collection: The sequence or iterable object to be indexed.
    :type collection: Iterable
    :yield: A tuple containing the current index and the corresponding item.
    :rtype: Generator[Tuple[int, Any], None, None]
    """
    i: int = 0

    for item in collection:
        yield i, item
        i += 1