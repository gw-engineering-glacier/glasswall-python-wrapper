

from psutil import Process, NoSuchProcess
from typing import Optional


def get_total_memory_usage_in_gib(pid: Optional[int]) -> float:
    """ Calculate the total memory usage of a process and its child processes in gigibytes (GiB).

    Args:
        pid (int, optional): The process ID for which memory usage is to be calculated. If None, returns 0.0.

    Returns:
        float: The total memory usage of the process and its children in GiB. If pid is None, returns 0.0.
    """
    if pid is None:
        return 0.0

    try:
        psutil_process = Process(pid)
    except NoSuchProcess:
        # Handle the case where the process does not exist
        return 0.0

    total_memory = psutil_process.memory_info().rss

    # Include memory usage of child processes
    for child in psutil_process.children(recursive=True):
        total_memory += child.memory_info().rss

    return total_memory / 1024 ** 3  # Convert bytes to GiB
