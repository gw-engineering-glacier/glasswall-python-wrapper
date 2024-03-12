

import unittest
from multiprocessing import Queue

from glasswall.multiprocessing.tasks import Task, TaskResult, execute_task_and_put_in_queue


def sample_function(x, n=2):
    return x * n


class TestTasks(unittest.TestCase):
    def test_task_creation(self):
        # Test task creation
        def sample_task():
            return "Hello, world!"

        task = Task(sample_task)
        self.assertEqual(task.func, sample_task)
        self.assertEqual(task.args, ())
        self.assertEqual(task.kwargs, {})

    def test_task_creation_with_args_and_kwargs(self):
        # Test task creation with arguments and keyword arguments
        def sample_task_with_args(arg1, arg2, kwarg1=None):
            return f"Arguments: {arg1}, {arg2}. Keyword Argument: {kwarg1}"

        args = (10, 20)
        kwargs = {"kwarg1": "test"}
        task = Task(sample_task_with_args, args=args, kwargs=kwargs)
        self.assertEqual(task.func, sample_task_with_args)
        self.assertEqual(task.args, args)
        self.assertEqual(task.kwargs, kwargs)

    def test_task_result_creation(self):
        # Test task result creation
        task = Task(sample_function, args=(5,))
        task_result = TaskResult(task, success=True, result=10)
        self.assertEqual(task_result.task, task)
        self.assertTrue(task_result.success)
        self.assertEqual(task_result.result, 10)
        self.assertIsNone(task_result.exception)

    def test_execute_task_and_put_in_queue(self):
        # Test executing a task and putting it into the queue
        queue: "Queue[TaskResult]" = Queue()
        task = Task(sample_function, args=(5,))
        execute_task_and_put_in_queue(task, queue)
        task_result = queue.get()
        self.assertTrue(task_result.success)
        self.assertEqual(task_result.result, 10)

        # After getting from the queue, it should be empty
        self.assertTrue(queue.empty())

        # Additional check to ensure the task result matches the expected task
        self.assertEqual(task_result.task, task)


if __name__ == "__main__":
    unittest.main()
