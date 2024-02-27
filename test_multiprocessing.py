

import os
import time

from tqdm import tqdm

import glasswall
from glasswall.multiprocessing import GlasswallProcessManager, Task

# INPUT_DIRECTORY = "/mnt/langley_test/langley_test_set_safe"
# OUTPUT_DIRECTORY = "output"
# LIBRARY_DIRECTORY = "/home/azureuser/langley_test/releases/10.0"
INPUT_DIRECTORY = r"C:\Users\AngusRoberts\Desktop\langley_multiprocessing\input_supported\document\docx"
OUTPUT_DIRECTORY = "output"
LIBRARY_DIRECTORY = r"C:\Users\AngusRoberts\Desktop\langley_multiprocessing\releases\10.0"

glasswall.config.logging.console.setLevel("CRITICAL")
EDITOR = glasswall.Editor(LIBRARY_DIRECTORY)


def worker_function(*args, **kwargs):
    EDITOR.export_file(*args, **kwargs)


def main():
    start_time = time.time()
    input_files = glasswall.utils.list_file_paths(INPUT_DIRECTORY)
    with GlasswallProcessManager(max_workers=None, worker_timeout_seconds=5) as process_manager:
        for input_file in tqdm(input_files, desc="Queueing files"):
            relative_path = os.path.relpath(input_file, INPUT_DIRECTORY)
            output_file = os.path.join(OUTPUT_DIRECTORY, relative_path)

            task = Task(
                func=worker_function,
                args=None,
                kwargs={
                    "input_file": input_file,
                    "output_file": output_file,
                },
            )
            process_manager.queue_task(task)

    print(f"Elapsed: {time.time() - start_time}")

    results = process_manager.task_results

    from collections import Counter
    exceptions = Counter(str(item.exception) if item else None for item in results)
    for k, v in exceptions.items():
        print(k, v)

    success = [item.success for item in results if item.success is True]
    failure = [item.success for item in results if item.success is False]
    print(f"Success: {len(success)}\nFailure: {len(failure)}")

    for task_result in results:
        print(task_result.__dict__)


if __name__ == "__main__":
    main()
