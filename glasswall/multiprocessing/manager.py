from multiprocessing import Process, Queue
import os
import time
from collections import deque
from typing import List, Optional

from tqdm import tqdm

from glasswall.multiprocessing.task_watcher import TaskWatcher
from glasswall.multiprocessing.tasks import Task, TaskResult


class GlasswallProcessManager:
    def __init__(
        self,
        max_workers: Optional[int] = None,
        worker_timeout_seconds: Optional[float] = None,
        memory_limit_in_gb: Optional[float] = None,
        sleep_time: Optional[float] = None,
    ):
        self.max_workers = max_workers or os.cpu_count() or 1
        self.worker_timeout_seconds = worker_timeout_seconds
        self.memory_limit_in_gb = memory_limit_in_gb
        self.sleep_time = sleep_time

        self.pending_processes: "deque[Process]" = deque()
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
            kwargs={
                "task": task,
                "task_results_queue": self.task_results_queue,
                "timeout_seconds": self.worker_timeout_seconds,
                "memory_limit_in_gb": self.memory_limit_in_gb,
            },
        )
        self.pending_processes.append(process)

    def clean_task_results_queue(self):
        while not self.task_results_queue.empty():
            self.task_results.append(self.task_results_queue.get())

    def remove_completed_active_processes(self, pbar: tqdm):
        index = 0
        while index < len(self.active_processes):
            process = self.active_processes[index]
            if not process.is_alive():
                process.join()
                self.active_processes.remove(process)
                pbar.update(1)
                self.clean_task_results_queue()
            else:
                index += 1

    def wait_for_completed_process(self, pbar: tqdm):
        self.remove_completed_active_processes(pbar)
        while len(self.active_processes) >= self.max_workers:
            self.remove_completed_active_processes(pbar)
            if self.sleep_time:
                time.sleep(self.sleep_time)

    def start_tasks(self):
        with tqdm(total=len(self.pending_processes), desc="Processing tasks") as pbar:
            while self.pending_processes or len(self.active_processes) > 0:
                if self.active_processes:
                    self.wait_for_completed_process(pbar)

                while len(self.active_processes) < self.max_workers and self.pending_processes:
                    process = self.pending_processes.popleft()
                    self.active_processes.append(process)
                    process.start()
