import time
import logging
import functools
import random
from typing import Callable, Any, Dict, List, Optional, TypeVar, cast

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

T = TypeVar('T')

def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    max_delay: float = 60.0,
    errors: tuple = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Retry a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries.
        initial_delay: Initial delay in seconds.
        exponential_base: Base of the exponential backoff.
        jitter: Whether to add jitter to the delay.
        max_delay: Maximum delay in seconds.
        errors: Tuple of exceptions to catch and retry.
    
    Returns:
        Decorator function.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            num_retries = 0
            delay = initial_delay
            
            while True:
                try:
                    return func(*args, **kwargs)
                except errors as e:
                    num_retries += 1
                    if num_retries > max_retries:
                        logger.error(f"Maximum retries ({max_retries}) exceeded. Last error: {e}")
                        raise
                    
                    delay = min(delay * exponential_base, max_delay)
                    if jitter:
                        delay = delay * (0.5 + random.random())
                    
                    logger.warning(f"Retry {num_retries}/{max_retries} after {delay:.2f}s. Error: {e}")
                    time.sleep(delay)
        
        return cast(Callable[..., T], wrapper)
    
    return decorator

def safe_execute(func: Callable, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Safely execute a function and return a dictionary with the result or error.
    
    Args:
        func: Function to execute.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.
    
    Returns:
        Dictionary with the result or error.
    """
    try:
        result = func(*args, **kwargs)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {e}")
        return {"success": False, "error": str(e)}

def batch_with_error_handling(items: List[Any], process_func: Callable[[Any], Any], batch_size: int = 5) -> Dict[str, Any]:
    """
    Process items in batches with error handling.
    
    Args:
        items: List of items to process.
        process_func: Function to process each item.
        batch_size: Size of each batch.
    
    Returns:
        Dictionary with results and errors.
    """
    results = []
    errors = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(items) + batch_size - 1)//batch_size}")
        
        for item in batch:
            result = safe_execute(process_func, item)
            if result["success"]:
                results.append(result["result"])
            else:
                errors.append({"item": item, "error": result["error"]})
    
    return {
        "success_count": len(results),
        "error_count": len(errors),
        "results": results,
        "errors": errors
    }

# Example usage:
# @retry_with_exponential_backoff(max_retries=5, initial_delay=2.0)
# def fetch_data_from_api(url: str) -> Dict[str, Any]:
#     response = requests.get(url)
#     response.raise_for_status()
#     return response.json()

if __name__ == "__main__":
    # Example usage
    @retry_with_exponential_backoff(max_retries=3)
    def example_function(value: int) -> int:
        if value < 0:
            raise ValueError("Value must be non-negative")
        return value * 2
    
    # Test successful execution
    try:
        result = example_function(5)
        print(f"Success: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test retry and failure
    try:
        result = example_function(-1)
        print(f"Success: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test batch processing
    items = [1, 2, -1, 4, -2, 6]
    result = batch_with_error_handling(items, lambda x: x * 2 if x > 0 else ValueError(f"Invalid value: {x}"))
    print(f"Batch result: {result}")
