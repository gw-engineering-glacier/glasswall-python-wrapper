

import os
import time
from collections import deque
from multiprocessing import Process, Queue
from typing import List, Generator, Optional

from glasswall.multiprocessing.task_watcher import TaskWatcher
from glasswall.multiprocessing.tasks import Task, TaskResult


class GlasswallProcessManager:
    def __init__(
        self,
        max_workers: Optional[int] = None,
        worker_timeout_seconds: Optional[float] = None,
        memory_limit_in_gib: Optional[float] = None,
    ):
        self.max_workers = max_workers or os.cpu_count() or 1
        self.worker_timeout_seconds = worker_timeout_seconds
        self.memory_limit_in_gib = memory_limit_in_gib
        self._sleep_time: float = 0  # Time to sleep for while waiting for processes to complete
        self._task_watcher_sleep_time: float = 0.001  # Time the TaskWatcher sleeps for while waiting for completed processes and monitoring timeout/memory
        self._task_watcher_memory_limit_polling_rate: float = 0.1  # Polling rate for TaskWatcher to check the memory usage of a process

        self.pending_processes: deque[Process] = deque()
        self.active_processes: list[Process] = []
        self.task_results_queue: "Queue[TaskResult]" = Queue()
        self.task_results: List[TaskResult] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.start_tasks()

    def queue_task(self, task: Task):
        # Create and queue the process without starting it
        process = Process(
            target=TaskWatcher,
            kwargs=dict(
                task=task,
                task_results_queue=self.task_results_queue,
                timeout_seconds=self.worker_timeout_seconds,
                memory_limit_in_gib=self.memory_limit_in_gib,
                sleep_time=self._task_watcher_sleep_time,
                memory_limit_polling_rate=self._task_watcher_memory_limit_polling_rate,
            ),
        )
        self.pending_processes.append(process)

    def as_completed(self) -> Generator[TaskResult, None, None]:
        while self.pending_processes or self.active_processes:
            if self.active_processes:
                self.wait_for_completed_process()

            while len(self.active_processes) < self.max_workers and self.pending_processes:
                process = self.pending_processes.popleft()
                self.active_processes.append(process)
                process.start()

            for result in self.task_results:
                self.task_results.remove(result)
                yield result

    def start_tasks(self):
        self.task_results = list(self.as_completed())

    def wait_for_completed_process(self):
        self.remove_completed_active_processes()
        while len(self.active_processes) >= self.max_workers:
            if self._sleep_time:
                time.sleep(self._sleep_time)
            self.remove_completed_active_processes()

    def remove_completed_active_processes(self):
        self.active_processes = [process for process in self.active_processes if process.is_alive()]
        self.clean_task_results_queue()

    def clean_task_results_queue(self):
        while not self.task_results_queue.empty():
            self.task_results.append(self.task_results_queue.get())
