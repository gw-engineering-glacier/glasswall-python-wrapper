

import time
import unittest
from multiprocessing import Queue

from glasswall.multiprocessing.task_watcher import TaskWatcher
from glasswall.multiprocessing.tasks import Task, TaskResult


def sample_task() -> str:
    return "Task completed!"


def long_running_task() -> None:
    time.sleep(1)


def exception_task() -> None:
    raise ValueError("Test exception")


class TestTaskWatcher(unittest.TestCase):
    def test_task_watcher_auto_start(self):
        # Test task watcher with auto_start=True
        task = Task(sample_task)
        queue: "Queue[TaskResult]" = Queue()
        TaskWatcher(task, queue)
        task_result = queue.get()
        self.assertTrue(task_result.success)
        self.assertEqual(task_result.result, "Task completed!")

    def test_task_watcher_manual_start(self):
        # Test task watcher with auto_start=False
        task = Task(sample_task)
        queue: "Queue[TaskResult]" = Queue()
        watcher = TaskWatcher(task, queue, auto_start=False)
        watcher.start_task()
        watcher.watch_task()
        watcher.update_queue()
        task_result = queue.get()
        self.assertTrue(task_result.success)
        self.assertEqual(task_result.result, "Task completed!")

    def test_task_watcher_timeout(self):
        # Test task watcher with timeout
        task = Task(long_running_task)
        queue: "Queue[TaskResult]" = Queue()
        TaskWatcher(task, queue, timeout_seconds=0.1)
        task_result = queue.get()
        self.assertFalse(task_result.success)
        self.assertIsInstance(task_result.exception, TimeoutError)

    def test_task_watcher_exception(self):
        # Test task watcher with task raising an exception
        task = Task(exception_task)
        queue: "Queue[TaskResult]" = Queue()
        TaskWatcher(task, queue)
        task_result = queue.get()
        self.assertFalse(task_result.success)
        self.assertIsInstance(task_result.exception, ValueError)
        self.assertIn("Test exception", str(task_result.exception))


if __name__ == "__main__":
    unittest.main()
