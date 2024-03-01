import time
from multiprocessing import Process, Queue
from typing import Optional

from psutil import NoSuchProcess
from psutil import Process as PsutilProcess

from glasswall.multiprocessing.deletion import force_object_under_target_size
from glasswall.multiprocessing.tasks import Task, TaskResult, execute_task_and_put_in_queue
from glasswall.utils import round_up


def get_total_memory_in_gb(process: Process) -> float:
    total_memory: float = 0
    try:
        psutil_process = PsutilProcess(process.pid)
        total_memory = psutil_process.memory_info().rss

        # Include memory usage of child processes
        for child in psutil_process.children(recursive=True):
            total_memory += child.memory_info().rss

        return total_memory / 1024 ** 3  # Convert bytes to GB

    except NoSuchProcess:
        # Handle the case where the process does not exist
        return 0.0


class TaskWatcher:
    process: Process
    start_time: float
    end_time: float
    elapsed_time: float

    def __init__(
        self,
        task: Task,
        task_results_queue: "Queue[TaskResult]",
        timeout_seconds: Optional[float] = None,
        memory_limit_in_gb: Optional[float] = None,
        sleep_time: float = 0.001,
        sleep_time_memory_limit: float = 1,
        auto_start: bool = True,
    ):
        self.task = task
        self.task_results_queue = task_results_queue
        self.timeout_seconds = timeout_seconds
        self.memory_limit_in_gb = memory_limit_in_gb
        self.sleep_time = sleep_time
        self.sleep_time_memory_limit = sleep_time_memory_limit
        self.auto_start = auto_start

        self.watcher_queue: "Queue[TaskResult]" = Queue()

        self.exception = None
        self.timed_out: bool = False
        self.out_of_memory: bool = False

        if self.auto_start:
            self.start_task()
            self.watch_task()
            self.update_queue()

    def start_task(self) -> None:
        self.process = Process(
            target=execute_task_and_put_in_queue,
            args=(self.task, self.watcher_queue,)
        )
        self.process.start()
        self.start_time = time.time()

    def terminate_task(self) -> None:
        self.process.terminate()

    def terminate_task_with_timeout(self) -> None:
        self.terminate_task()
        self.timed_out = True
        self.exception = TimeoutError()

    def terminate_task_with_out_of_memory(self) -> None:
        self.terminate_task()
        self.out_of_memory = True
        self.exception = MemoryError()

    def watch_task(self) -> None:
        last_memory_limit_check = time.time()
        while self.process.is_alive():
            # Monitor for timeout exceeded
            if self.timeout_seconds:
                if time.time() - self.start_time > self.timeout_seconds:
                    self.terminate_task_with_timeout()
                    break

            # Monitor for memory limit exceeded
            if self.memory_limit_in_gb:
                if time.time() - last_memory_limit_check > self.sleep_time_memory_limit:
                    last_memory_limit_check = time.time()
                    memory_usage_in_gb = get_total_memory_in_gb(process=self.process)
                    if memory_usage_in_gb > self.memory_limit_in_gb:
                        self.terminate_task_with_out_of_memory()
                        break

            if self.sleep_time:
                time.sleep(self.sleep_time)

        self.end_time = time.time()
        self.elapsed_time = round_up(self.end_time - self.start_time, decimals=2)
        self.process.join()

    def update_queue(self) -> None:
        if self.exception:
            # TimeoutError or MemoryError
            task_result = TaskResult(
                self.task,
                success=False,
                exception=self.exception,
            )  # TODO add memoryusage
        else:
            task_result = self.watcher_queue.get()

        task_result.task = self.task
        task_result.timeout_seconds = self.timeout_seconds
        task_result.memory_limit_in_gb = self.memory_limit_in_gb

        task_result.start_time = self.start_time
        task_result.end_time = self.end_time
        task_result.elapsed_time = self.elapsed_time
        task_result.timed_out = self.timed_out
        task_result.out_of_memory = self.out_of_memory

        # Ensure task_result can fit in queue
        task_result = force_object_under_target_size(task_result, target_size=8192)

        self.task_results_queue.put(task_result)
