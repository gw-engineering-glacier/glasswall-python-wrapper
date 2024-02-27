

import time
from multiprocessing import Process, Queue
from typing import Optional

from glasswall.multiprocessing.tasks import Task, TaskResult, execute_task_and_put_in_queue


class TaskWatcher:
    def __init__(self, task: Task, task_results_queue: Queue, timeout_seconds: Optional[int] = None, sleep_time: Optional[float] = 0.001):
        self.task = task
        self.task_results_queue = task_results_queue
        self.timeout_seconds = timeout_seconds
        self.sleep_time = sleep_time

        self.watcher_queue = Queue()

        self.process: Process = None
        self.start_time: float = None
        self.end_time: float = None
        self.elapsed_time: float = None
        self.timed_out = False
        self.out_of_memory = False
        self.exception: Exception = None

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
        self.exception = TimeoutError

    def terminate_task_with_out_of_memory(self) -> None:
        self.terminate_task()
        self.out_of_memory = True
        self.exception = MemoryError

    def watch_task(self) -> None:
        while self.process.is_alive():
            # Monitor for timeout exceeded
            if self.timeout_seconds:
                if time.time() - self.start_time > self.timeout_seconds:
                    self.terminate_task_with_timeout()
                    break

            # Monitor for memory limit exceeded
            # TODO

            if self.sleep_time:
                time.sleep(self.sleep_time)

        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        self.process.join()

    def update_queue(self) -> None:
        if self.exception:
            # TimeoutError or MemoryError
            task_result = TaskResult(self.task, success=False, exception=self.exception)  # TODO add memoryusage
        else:
            task_result = self.watcher_queue.get()

        task_result.task = self.task
        task_result.timeout_seconds = self.timeout_seconds

        task_result.start_time = self.start_time
        task_result.end_time = self.end_time
        task_result.elapsed_time = self.elapsed_time
        task_result.timed_out = self.timed_out
        # task_result.out_of_memory = self.out_of_memory # TODO

        self.task_results_queue.put(task_result)
