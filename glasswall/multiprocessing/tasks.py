

from multiprocessing import Queue
from typing import Any, Callable, Optional, Union


class Task:
    def __init__(self, func: Callable, args: Optional[tuple] = None, kwargs: Optional[dict] = None):
        self.func = func
        self.args = args or tuple()
        self.kwargs = kwargs or dict()


class TaskResult:
    def __init__(self, task: Task, success: bool, result: Any = None, exception: Union[Exception, None] = None):
        self.task = task
        self.success = success
        self.result = result
        self.exception = exception


def execute_task_and_put_in_queue(task: Task, queue: Queue) -> None:
    try:
        func_result = task.func(*task.args, **task.kwargs)
        task_result = TaskResult(task=task, success=True, result=func_result)
    except Exception as e:
        task_result = TaskResult(task=task, success=False, exception=e)
    queue.put(task_result)
