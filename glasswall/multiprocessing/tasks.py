

from multiprocessing import Queue
from typing import Any, Callable, Optional, Union

import glasswall


class Task:
    def __init__(
        self,
        func: Callable,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
    ):
        self.func = func
        self.args = args or tuple()
        self.kwargs = kwargs or dict()

        # Convert Policy objects to text (has attributes that are modules, and modules cannot be pickled)
        # args
        processed_args = []
        for arg in self.args:
            if isinstance(arg, glasswall.content_management.policies.Policy):
                arg = arg.text
            processed_args.append(arg)
        self.args = tuple(processed_args)
        # kwargs
        for key, value in self.kwargs.items():
            if isinstance(value, glasswall.content_management.policies.Policy):
                self.kwargs[key] = value.text

    def __eq__(self, other):
        if isinstance(other, Task):
            return (self.func, self.args, self.kwargs) == (other.func, other.args, other.kwargs)
        return False

    def __hash__(self):
        kwargs_tuple = tuple(sorted(self.kwargs.items()))
        return hash((self.func, self.args, kwargs_tuple))

    def __repr__(self):
        max_length = 100
        args_str = ", ".join(repr(arg)[:max_length] + ('...' if len(repr(arg)) > max_length else '') for arg in self.args)
        kwargs_str = ", ".join(f"{key}={repr(value)[:max_length] + ('...' if len(repr(value)) > max_length else '')}" for key, value in self.kwargs.items())
        return f"{self.__class__.__name__}(func={self.func.__name__}, args=({args_str}), kwargs=({kwargs_str}))"


class TaskResult:
    timeout_seconds: Optional[float]
    memory_limit_in_gib: Optional[float]
    start_time: float
    end_time: float
    elapsed_time: float
    out_of_memory: bool
    timed_out: bool
    max_memory_used_in_gib: float
    exit_code: Union[int, None]

    def __init__(
        self,
        task: Task,
        success: bool,
        result: Any = None,
        exception: Union[Exception, None] = None,
    ):
        self.task = task
        self.success = success
        self.result = result
        self.exception = exception

    def __eq__(self, other):
        if isinstance(other, TaskResult):
            return (self.task, self.success, self.result, self.exception) == \
                (other.task, other.success, other.result, other.exception)
        return False

    def __hash__(self):
        return hash((self.task, self.success, self.result, self.exception))

    def __repr__(self):
        max_length = 100
        attributes_str = ', '.join(f"{k}={v!r}"[:max_length] + ('...' if len(repr(v)) > max_length else '') for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attributes_str})"


def execute_task_and_put_in_queue(task: Task, queue: "Queue[TaskResult]") -> None:
    try:
        func_result = task.func(*task.args, **task.kwargs)
        task_result = TaskResult(task=task, success=True, result=func_result)
    except Exception as e:
        task_result = TaskResult(task=task, success=False, exception=e)

    queue.put(task_result)
