import argparse
import os
import sys
import time
import unittest
from collections import Counter

from tqdm import tqdm

import glasswall
from glasswall.config.logging import log
from glasswall.multiprocessing import GlasswallProcessManager, Task

glasswall.config.logging.console.setLevel("CRITICAL")


def worker_function(*args, **kwargs):
    library_name = os.environ["GLASSWALL_LIBRARY_NAME"]
    function_name = os.environ["GLASSWALL_FUNCTION_NAME"]
    library_path = os.environ["GLASSWALL_LIBRARY_PATH"]
    library_class = getattr(glasswall, library_name)
    library = library_class(library_path)
    library_function = getattr(library, function_name)
    library_function(*args, **kwargs)


class TestIntegration(unittest.TestCase):
    input_directory: str
    output_directory: str
    library_directory: str
    max_workers: int
    timeout: float
    library_name: str
    function_name: str

    @classmethod
    def setUpClass(cls):
        cls.input_directory = os.environ["GLASSWALL_INPUT_PATH"]
        cls.output_directory = os.environ["GLASSWALL_OUTPUT_PATH"]
        cls.library_directory = os.environ["GLASSWALL_LIBRARY_PATH"]
        if "GLASSWALL_MAX_WORKERS" in os.environ.keys():
            cls.max_workers = int(os.environ["GLASSWALL_MAX_WORKERS"])
        else:
            cls.max_workers = os.cpu_count() or 1
        cls.timeout = float(os.environ["GLASSWALL_TIMEOUT"])
        cls.memory_limit_in_gib = int(os.environ["GLASSWALL_MEMORY_LIMIT_IN_GIB"])
        cls.library_name = os.environ["GLASSWALL_LIBRARY_NAME"]
        cls.function_name = os.environ["GLASSWALL_FUNCTION_NAME"]
        cls.multiply_dataset = int(os.environ["GLASSWALL_MULTIPLY_DATASET"])

        print(f"input_directory:{cls.input_directory}")
        print(f"output_directory:{cls.output_directory}")
        print(f"library_directory:{cls.library_directory}")
        print(f"max_workers:{cls.max_workers}")
        print(f"timeout:{cls.timeout}")
        print(f"library_name:{cls.library_name}")
        print(f"function_name:{cls.function_name}")

        if not os.path.isdir(cls.input_directory):
            raise NotADirectoryError(cls.input_directory)

        if not os.path.isdir(cls.output_directory):
            os.makedirs(cls.output_directory, exist_ok=True)

        if not os.path.isdir(cls.library_directory) and not os.path.isfile(
            cls.library_directory
        ):
            raise NotADirectoryError(cls.library_directory)

        if not hasattr(glasswall.Editor, cls.function_name):
            raise AttributeError(cls.function_name)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_integration(self):
        input_files = glasswall.utils.list_file_paths(self.input_directory)
        if self.multiply_dataset:
            input_files *= self.multiply_dataset

        start_time = time.time()
        with GlasswallProcessManager(
            max_workers=self.max_workers,
            worker_timeout_seconds=self.timeout,
            memory_limit_in_gib=self.memory_limit_in_gib,
        ) as process_manager:
            for input_file in tqdm(input_files, desc="Queueing files", miniters=len(input_files) // 10):
                relative_path = os.path.relpath(input_file, self.input_directory)
                output_file = os.path.normpath(
                    os.path.join(self.output_directory, relative_path)
                )

                task = Task(
                    func=worker_function,
                    args=None,
                    kwargs={
                        "input_file": input_file,
                        "output_file": output_file,
                    },
                )
                process_manager.queue_task(task)

            results = []
            for task_result in tqdm(process_manager.as_completed(), total=len(input_files), desc="Processing tasks", miniters=len(input_files) // 100):
                results.append(task_result)

        end_time = time.time()

        # Reenable logging
        glasswall.config.logging.console.setLevel("INFO")

        log.info(f"Elapsed: {end_time - start_time}")

        log.info("Exceptions:")
        exceptions = Counter(str(item.exception) if item else None for item in results)
        for k, v in exceptions.items():
            log.info(f"{k} = {v}")

        success = [item.success for item in results if item.success is True]
        failure = [item.success for item in results if item.success is False]
        log.info(f"Success: {len(success)}")
        log.info(f"Failure: {len(failure)}")

        self.assertFalse(all(result.success is False for result in results), msg="All 'success' attributes are False.")

        for task_result in results:
            log.info(task_result.__dict__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-directory", required=True, type=str)
    parser.add_argument("--output-directory", required=True, type=str)
    parser.add_argument("--library-directory", required=True, type=str)
    parser.add_argument("--max-workers", required=True, type=int)
    parser.add_argument("--timeout", required=True, type=float)
    parser.add_argument("--memory-limit-in-gib", default="0", type=int)
    parser.add_argument("--library-name", default="Editor", type=str)
    parser.add_argument("--function-name", default="export_file", type=str)
    parser.add_argument("--multiply-dataset", default="1", type=int)
    args = parser.parse_args()

    os.environ["GLASSWALL_INPUT_PATH"] = str(args.input_directory)
    os.environ["GLASSWALL_OUTPUT_PATH"] = str(args.output_directory)
    os.environ["GLASSWALL_LIBRARY_PATH"] = str(args.library_directory)
    os.environ["GLASSWALL_MAX_WORKERS"] = str(args.max_workers)
    os.environ["GLASSWALL_TIMEOUT"] = str(args.timeout)
    os.environ["GLASSWALL_MEMORY_LIMIT_IN_GIB"] = str(args.memory_limit_in_gib)
    os.environ["GLASSWALL_LIBRARY_NAME"] = str(args.library_name)
    os.environ["GLASSWALL_FUNCTION_NAME"] = str(args.function_name)
    os.environ["GLASSWALL_MULTIPLY_DATASET"] = str(args.multiply_dataset)

    # Set environment variables for worker_function to avoid below error via subclassing unittest.TestCase
    # TypeError: cannot pickle '_io.TextIOWrapper' object

    # unittest needs a clean sys.argv
    while len(sys.argv) > 1:
        sys.argv.pop()

    unittest.main()
