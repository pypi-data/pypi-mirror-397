"""
Decorators for function modification and metadata management.

This module provides various decorators for timing, caching, legacy
function warnings, and other function modifications.
"""

from __future__ import annotations
from typing import Callable, Tuple, Any, Type, Dict, Optional
import time
from warnings import warn

def mimic(wrapped: Callable[..., Any]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator factory to copy metadata from `wrapped` to wrapper function.
    
    Copies function metadata such as name, docstring, annotations, and
    dictionary entries from the wrapped function to the wrapper.
    
    :param wrapped: The function whose metadata should be copied.
    :type wrapped: Callable[..., Any]
    :return: A decorator that applies the metadata copying.
    :rtype: Callable[[Callable[..., Any]], Callable[..., Any]]
    """
    WRAPPER_ASSIGNED: Tuple[str, ...] = ('__module__', '__name__', '__qualname__', '__doc__', '__annotations__')
    WRAPPER_UPDATED: Tuple[str, ...] = ('__dict__',)

    def decorator(wrapper: Callable[..., Any]) -> Callable[..., Any]:
        for attr in WRAPPER_ASSIGNED:
            try:
                value = getattr(wrapped, attr)
                setattr(wrapper, attr, value)
            except AttributeError:
                pass
        
        for attr in WRAPPER_UPDATED:
            try:
                wrapper_dict = getattr(wrapper, attr)
                wrapped_dict = getattr(wrapped, attr)
                wrapper_dict.update(wrapped_dict)
            except AttributeError:
                pass
        
        wrapper.__wrapped__ = wrapped # type: ignore
        
        return wrapper

    return decorator

def timed(func: Callable[..., Any], announce: bool = False) -> Callable[..., Any]:
    """
    Measures execution time of a function.
    
    :param func: The function to time.
    :type func: Callable[..., Any]
    :param announce: If True, prints timing information to stdout.
                     If False, returns a tuple of (result, duration).
    :type announce: bool
    :return: Wrapped function that measures execution time.
    :rtype: Callable[..., Any]
    """
    @mimic(func)
    def wrapper(*args, **kwargs):
        start: float = time.perf_counter()
        result: Any = func(*args, **kwargs)
        duration: float = time.perf_counter() - start

        if announce:
            print(f"[timer] '{func.__name__}' took {duration:.3f} seconds to run")
            return result
        
        return result, duration
    return wrapper

def repeat(func: Callable[..., Any], *args, **kwargs) -> Callable[..., Any]:
    """
    Creates a function factory that returns a decorator.
    
    The final call (count) dictates how many times 'func' is executed.
    Syntax: `repeat(func, *setup_args)(count)`
    
    :param func: The function that will be executed repeatedly.
    :type func: Callable[..., Any]
    :param args: Arguments to pass to the function on each execution.
    :type args: Any
    :param kwargs: Keyword arguments to pass to the function on each execution.
    :type kwargs: Any
    :return: A function waiting for the 'count' argument.
    :rtype: Callable[..., Any]
    """
    from metrima.lib import span
    
    def count_handler(count: int = 3):
        """
        Accepts the 'count' argument and returns the wrapper.
        
        :param count: Number of times to execute the function.
        :type count: int
        :return: Wrapper function that executes the function count times.
        :rtype: Callable[..., Any]
        """
        
        def wrapper(*w_args, **w_kwargs):
            last_result: Any = None
            
            for _ in span(count):
                last_result = func(*args, **kwargs)

            return last_result
        
        return wrapper
    
    return count_handler

def memo(clean: bool | Callable[..., Any] = True, max_cache: int = 5) -> Callable[..., Any]:
    """
    Memoization decorator with cache management.
    
    :param clean: If True, cleans cache when it exceeds max_cache.
                  If a callable is provided, applies memoization to it.
    :type clean: bool | Callable[..., Any]
    :param max_cache: Maximum number of cached results to keep.
    :type max_cache: int
    :return: Memoization decorator or decorated function.
    :rtype: Callable[..., Any]
    """
    if callable(clean):
        return memo(clean=True, max_cache=10)(clean) # type: ignore

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache: Dict[Tuple[Any, ...], Any] = {}

        @mimic(func)
        def wrapper(*args, **kwargs):
            key: Tuple = args + tuple(sorted(kwargs.items()))

            if key in cache:
                return cache[key]
            
            result = func(*args, **kwargs)
            cache[key] = result
            
            if clean and len(cache) > max_cache:
                del cache[next(iter(cache))]
            return result
        
        return wrapper
    return decorator

def legacy(message: str = "This is a legacy function and may behave "
            "differently from the updated version.") -> Callable[..., Any]:
    """
    Decorator to mark functions as legacy with deprecation warnings.
    
    :param message: Warning message to display when function is called.
    :type message: str
    :return: Decorator that adds deprecation warnings to functions.
    :rtype: Callable[..., Any]
    """
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @mimic(func)
        def wrapper(*args, **kwargs):
            warn(message, DeprecationWarning, stacklevel=2)

            result = func(*args, **kwargs)
            return result
        return wrapper
    
    return decorator

def once(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to make a method callable only once.
    
    :param func: The method to decorate.
    :type func: Callable[..., Any]
    :return: The decorated method.
    :rtype: Callable[..., Any]
    :raises RuntimeError: If the method is called more than once.
    """
    @mimic(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, '_once_called'):
            self._once_called = set()
        
        if func.__name__ in self._once_called:
            raise RuntimeError(f"{func.__name__} can only be called once")
        
        self._once_called.add(func.__name__)
        return func(self, *args, **kwargs)
    return wrapper

class attribute:
    """
    Acts as a descriptor that handles attribute access, assignment, and deletion.
    
    This class implements the descriptor protocol to create managed
    attributes with custom getter, setter, and deleter functions.
    """
    def __init__(self, fget: Callable[[Any], Any],
                 fset: Optional[Callable[[Any, Any], None]] = None,
                 fdel: Optional[Callable[[Any], None]] = None) -> None:
        """
        Initialize an attribute descriptor.
        
        :param fget: Getter function for the attribute.
        :type fget: Callable[[Any], Any]
        :param fset: Setter function for the attribute (optional).
        :type fset: Optional[Callable[[Any, Any], None]]
        :param fdel: Deleter function for the attribute (optional).
        :type fdel: Optional[Callable[[Any], None]]
        """
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def __get__(self, inst: Any, owner: Type[Any]) -> Any:
        """
        Handles attribute retrieval.
        
        :param inst: The instance the attribute is accessed on.
        :type inst: Any
        :param owner: The owner class of the attribute.
        :type owner: Type[Any]
        :return: The attribute value.
        :rtype: Any
        :raises AttributeError: If the attribute is not readable.
        """
        if inst is None:
            return self

        if self.fget is None:
            raise AttributeError("unreadable attribute")
        
        return self.fget(inst)

    def __set__(self, instance: Any, value: Any) -> None:
        """
        Handles attribute assignment (e.g., instance.attr = value).
        
        :param instance: The instance to set the attribute on.
        :type instance: Any
        :param value: The value to set.
        :type value: Any
        :raises AttributeError: If the attribute cannot be set.
        """
        if self.fset is None:
            raise AttributeError("can't set attribute")
        
        self.fset(instance, value)

    def __delete__(self, instance: Any) -> None:
        """
        Handles attribute deletion (e.g., del instance.attr).
        
        :param instance: The instance to delete the attribute from.
        :type instance: Any
        :raises AttributeError: If the attribute cannot be deleted.
        """
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        
        self.fdel(instance)

    def setter(self, fset: Callable[[Any, Any], None]) -> 'attribute':
        """
        Decorator method: returns a new Attribute instance with the new setter function.
        
        Used with the syntax: @attr.setter
        
        :param fset: New setter function.
        :type fset: Callable[[Any, Any], None]
        :return: New attribute descriptor with updated setter.
        :rtype: attribute
        """
        return attribute(self.fget, fset, self.fdel)

    def deleter(self, fdel: Callable[[Any], None]) -> 'attribute':
        """
        Decorator method: returns a new Attribute instance with the new deleter function.
        
        Used with the syntax: @attr.deleter
        
        :param fdel: New deleter function.
        :type fdel: Callable[[Any], None]
        :return: New attribute descriptor with updated deleter.
        :rtype: attribute
        """
        return attribute(self.fget, self.fset, fdel)

def main() -> None:
    """
    Demonstration function showing usage of decorators.
    
    This function provides examples of how to use the various decorators
    defined in this module.
    """
    from tinycolors import cprint, color, clib # type: ignore

    cprint("=" * 50, as_="bold white")
    cprint("Decorators Demo with TinyColors", as_="bold cyan")
    cprint("=" * 50, as_="bold white")
    print()

    # Legacy decorator demo
    cprint("Testing @legacy decorator:", as_="bold yellow")
    cprint("-" * 50, as_="bold white")
    
    @legacy(message="Use float-add instead")
    def add(a: int, b: int) -> int:
        return a + b
    
    cprint("Calling add(1, 1)...", as_="italic blue")
    cprint(f"Result: {color.bold}{add(1, 1)}{clib.reset}", as_="bold green on black")
    print()

    # Modern function demo
    cprint("Using modern float_add function:", as_="bold yellow")
    cprint("-" * 50, as_="bold white")
    
    def float_add(a: float, b: float) -> float:
        return round(a + b)

    cprint("Calling float_add(1.2, 3.15)...", as_="italic blue")
    cprint(f"Result: {color.bold}{float_add(1.2, 3.15)}{clib.reset}", as_="bold green on black")
    print()

    # Timed decorator demo
    cprint("Testing @timed decorator:", as_="bold yellow")
    cprint("-" * 50, as_="bold white")
    
    @timed
    def slow_operation(n: int) -> int:
        total = 0
        for i in range(n):
            total += i
        return total
    
    cprint("Calling slow_operation(1000000)...", as_="italic blue")
    result, duration = slow_operation(1000000)
    cprint(f"Result: {color.bold}{result}{clib.reset}", as_="bold green on black")
    cprint(f"Duration: {color.italic}{duration:.6f} seconds{clib.reset}", color="yellow")
    print()

    # Memo decorator demo
    cprint("Testing @memo decorator:", as_="bold yellow")
    cprint("-" * 50, as_="bold white")
    
    @memo
    def fibonacci(n: int) -> int:
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2) # type: ignore
    
    cprint("First call: fibonacci(30) - computing...", as_="italic blue")
    start_time = time.perf_counter()
    result3 = fibonacci(30)
    first_duration = time.perf_counter() - start_time
    cprint(f"Result: {color.bold}{result3}{clib.reset}", as_="bold green on black")
    cprint(f"Time taken: {color.italic}{first_duration:.6f} seconds{clib.reset}", color="yellow")
    print()
    
    cprint("Second call: fibonacci(30) - cached!", as_="italic blue")
    start_time = time.perf_counter()
    cached_duration = time.perf_counter() - start_time
    cprint(f"Result: {color.bold}{result3}{clib.reset}", as_="bold green on black")
    cprint(f"Time taken: {color.italic}{cached_duration:.9f} seconds{clib.reset}", color="cyan")
    
    cprint(f"Speedup: {color.bold}{first_duration / cached_duration if cached_duration > 0 else 0:.0f}x faster{clib.reset}", as_="bold bright green")
    print()
    
    cprint("Third call: fibonacci(28) - also cached (computed during first call)!", as_="italic blue")
    start_time = time.perf_counter()
    partial_duration = time.perf_counter() - start_time
    cprint(f"Result: {color.bold}{fibonacci(28)}{clib.reset}", as_="bold green on black")
    cprint(f"Time taken: {color.italic}{partial_duration:.9f} seconds{clib.reset}", color="cyan")
    print()

    cprint("=" * 50, as_="bold white")
    cprint("Demo Complete!", as_="bold cyan")
    cprint("=" * 50, as_="bold white")

if __name__ == "__main__":
    main()