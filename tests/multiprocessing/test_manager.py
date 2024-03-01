

import time
import unittest
from multiprocessing import Process

from glasswall.multiprocessing.manager import GlasswallProcessManager
from glasswall.multiprocessing.tasks import Task, TaskResult


def sample_task():
    return "Task completed!"


def exception_task():
    raise ValueError("Test exception")


class TestGlasswallProcessManager(unittest.TestCase):
    def test_queue_task(self):
        # Test queuing a task
        manager = GlasswallProcessManager(max_workers=2)
        self.assertEqual(len(manager.pending_processes), 0)
        task = Task(sample_task)
        manager.queue_task(task)
        self.assertEqual(len(manager.pending_processes), 1)
        pending_process = manager.pending_processes[0]
        self.assertIsInstance(pending_process, Process)
        self.assertEqual(task, pending_process._kwargs["task"])

    def test_start_tasks(self):
        # Test starting tasks
        manager = GlasswallProcessManager(max_workers=2)
        task = Task(sample_task)
        manager.queue_task(task)
        self.assertEqual(len(manager.pending_processes), 1)
        self.assertEqual(len(manager.active_processes), 0)
        manager.start_tasks()
        # start_tasks populates active_processes, but should be empty once tasks are done
        self.assertEqual(len(manager.pending_processes), 0)
        self.assertEqual(len(manager.active_processes), 0)

    def test_clean_task_results_queue(self):
        # Test cleaning task results queue
        manager = GlasswallProcessManager(max_workers=2)
        task1 = Task(sample_task)
        task2 = Task(sample_task)
        result1 = TaskResult(task1, success=True, result="Task 1 completed!")
        result2 = TaskResult(task2, success=True, result="Task 2 completed!")

        # Insert some task results into the queue
        manager.task_results_queue.put(result1)
        manager.task_results_queue.put(result2)

        # Introduce a small delay to prevent race condition
        time.sleep(0.1)

        # Ensure the queue is not empty before cleaning
        self.assertFalse(manager.task_results_queue.empty())

        # Clean the task results queue
        manager.clean_task_results_queue()

        # Ensure the queue is empty after cleaning
        self.assertTrue(manager.task_results_queue.empty())

        # Ensure task results are correctly appended to manager's task_results list
        self.assertEqual(len(manager.task_results), 2)


if __name__ == "__main__":
    unittest.main()
