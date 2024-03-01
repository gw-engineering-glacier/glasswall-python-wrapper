import functools
import sys
from typing import Callable, TypeVar


class Deleted:
    """ Object deemed too large for queue. """
    pass


def hash_dict(func: Callable):
    """Transform mutable dictionary into immutable"""
    class HashDict(dict):
        def __hash__(self):
            return hash(frozenset(self.items()))

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple([HashDict(arg) if isinstance(arg, dict) else arg for arg in args])
        kwargs = {k: HashDict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)
    return wrapped


@hash_dict
@functools.lru_cache(maxsize=None)  # Cache the sizes of objects
def get_size(obj: object) -> int:
    """Recursively find the total size in memory of an object."""
    if isinstance(obj, dict):
        # Convert dictionary items to a tuple of tuples (key, value)
        return sum(get_size(k) + get_size(v) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set)):
        # Iterate over elements and sum their sizes
        return sum(get_size(x) for x in obj)
    elif isinstance(obj, (str, bytes, int, float)):
        # For simple types, use sys.getsizeof
        return sys.getsizeof(obj)
    elif hasattr(obj, "__dict__"):
        # For custom objects, iterate over their attributes
        # Convert attributes to a tuple to ensure hashability
        return sum(get_size(attr) for attr in vars(obj).values())
    else:
        return sys.getsizeof(obj)


T = TypeVar("T")


def force_object_under_target_size(obj: T, target_size: int = 8192) -> T:
    """Delete objects within the given object until total size is <= target_size"""
    total_size = get_size(obj)
    if total_size > target_size:
        attrs = sorted(obj.__dict__.items(), key=lambda x: get_size(x[1]), reverse=True)
        while total_size > target_size and attrs:
            largest_obj, largest_value = attrs.pop(0)
            setattr(obj, largest_obj, Deleted())
            total_size -= get_size(largest_value)
        if total_size > target_size:
            # Shouldn't ever happen, but if task_result is still too big ungracefully exit instead of hanging
            raise Exception(f"TaskResult too big for queue.\nSize: '{get_size(obj)}'.\nDict: '{obj.__dict__}'")
    return obj
