

import unittest
from multiprocessing import Queue

from glasswall.multiprocessing.deletion import force_object_under_target_size, Deleted
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

    def test_delete_objects_result_exceeds_threshold(self):
        # Test case where task_result size exceeds the threshold
        task_result = TaskResult(
            task=None,
            success=True,
            result="A" * 8193,
        )

        # Delete objects until total size is <= 8192 bytes
        task_result = force_object_under_target_size(task_result, target_size=8192)

        # Assert that the result is an instance of Delete
        self.assertIsInstance(task_result.result, Deleted)

    def test_delete_objects_task_kwarg_exceeds_threshold(self):
        # Test case where task_result size exceeds the threshold
        task_result = TaskResult(
            task=Task(
                func=None,
                args=None,
                kwargs={"somekwarg": "A" * 8193}
            ),
            success=True,
            result="A" * 8193,
        )

        # Delete objects until total size is <= 8192 bytes
        task_result = force_object_under_target_size(task_result, target_size=8192)

        # Assert that the Task is an instance of Delete
        self.assertIsInstance(task_result.task, Deleted)

    def test_queue_task_result_exceeds_threshold(self):
        # Test case where task_result size exceeds the threshold
        # sample_function returns "A" * 8193
        task = Task(func=sample_function, args=("A",), kwargs={"n": 8193})
        queue: "Queue[TaskResult]" = Queue()

        # Execute the function
        execute_task_and_put_in_queue(task, queue)
        task_result = queue.get()

        # Assert that the result is an instance of Delete
        self.assertIsInstance(task_result.result, Deleted)


if __name__ == "__main__":
    unittest.main()
