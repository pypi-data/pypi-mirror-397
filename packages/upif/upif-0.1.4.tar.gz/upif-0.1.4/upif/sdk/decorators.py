import functools
from typing import Callable, Optional
from upif import guard 
# We import the singleton 'guard'. 
# NOTE: Users must ensure 'guard' is configured with modules.

def protect(task: str = "general", strictness: str = "standard"):
    """
    Decorator to automatically scan function arguments for injections.
    
    Usage:
        @protect(task="chat")
        def my_llm_func(prompt): ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Inspect Arguments (Naive approach: scan first string arg)
            new_args = list(args)
            
            # Simple heuristic: Scan the first positional argument if it's a string
            if new_args and isinstance(new_args[0], str):
                original = new_args[0]
                sanitized = guard.process_input(original, metadata={"task": task})
                if sanitized != original:
                    # If sanitized changed, we use it
                    new_args[0] = sanitized
            
            # TODO: Scan kwargs if needed
            
            # 2. Call Original Function
            result = func(*tuple(new_args), **kwargs)

            # 3. Inspect Output (New Feature)
            # Naive approach: Scan return if it is a string
            if isinstance(result, str):
                sanitized_result = guard.process_output(result, metadata={"task": task})
                return sanitized_result
            
            return result
        return wrapper
    return decorator
