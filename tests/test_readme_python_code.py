

import os
import subprocess
import unittest


def extract_python_blocks_from_readme(file_path):
    # Function to extract Python blocks from the README and return as a dictionary
    python_blocks = {}
    start_marker = "```py"   # Start marker for identifying Python code blocks in the README
    end_marker = "```"       # End marker for identifying Python code blocks in the README
    header_count = {}        # Dictionary to keep track of header occurrences

    # Read the content of the README.md file
    with open(file_path, "rb") as readme_file:
        readme_content = readme_file.read()

    readme_content = readme_content.decode("utf-8")

    start_index = 0
    while start_index != -1:
        # Find the next occurrence of the start_marker
        start_index = readme_content.find(start_marker, start_index)
        if start_index != -1:
            # Find the corresponding end index of the current Python block
            end_index = readme_content.find(end_marker, start_index + len(start_marker))
            if end_index != -1:
                # Find the header just before the current Python block
                header_start = readme_content.rfind("###", 0, start_index)
                header_end = readme_content.find("\n", header_start)
                header = readme_content[header_start:header_end].strip("#").strip()

                # Increment the count for the current header in the dictionary
                if header not in header_count:
                    header_count[header] = 1
                else:
                    header_count[header] += 1

                # Modify the header name to include a numbering system for subsequent blocks
                header_name = f"{header}" if header_count[header] == 1 else f"{header} ({header_count[header]})"
                # Extract the Python block and add it to the dictionary with the modified header name
                python_blocks[header_name] = readme_content[start_index + len(start_marker):end_index].strip()

            # Move the start_index to the next character after the current Python block
            start_index = end_index + len(end_marker)

    return python_blocks


def execute_python_block(python_code):
    try:
        # Execute the Python block in a separate process and capture the output
        return subprocess.run(["python", "-c", python_code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Execution failed with error: {e}")

        # If an error occurs, print the captured output (stdout and stderr)
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)

        raise


def count_python_blocks_in_readme(file_path):
    # Function to count the occurrences of "```py" in the README
    with open(file_path, "rb") as readme_file:
        readme_content = readme_file.read()

    readme_content = readme_content.decode("utf-8")

    return readme_content.count("```py")


class TestReadmeCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Extract Python blocks from the README and store them in a class-level variable
        readme_file_path = "README.md"
        cls.python_blocks_dict = extract_python_blocks_from_readme(readme_file_path)
        cls.python_blocks_count = count_python_blocks_in_readme(readme_file_path)

        if not os.path.exists("C:/gwpw/libraries"):
            raise unittest.SkipTest("No Glasswall libraries found.")

    def test_extract_python_blocks(self):
        # Test that the extract_python_blocks_from_readme function works as expected
        self.assertEqual(len(self.python_blocks_dict), self.python_blocks_count)

    def test_python_blocks_execution(self):
        # Test the execution of each Python block and assert that they pass successfully
        for header, block in self.python_blocks_dict.items():
            with self.subTest(header=header):
                print(f"Running subtest for header: '{header}'")
                result = execute_python_block(block)
                if isinstance(result, subprocess.CalledProcessError):
                    self.fail(f"Test '{header}' failed with error: {result}")
                else:
                    self.assertEqual(result.returncode, 0, f"Test '{header}' failed with a non-zero exit code.")


if __name__ == "__main__":
    unittest.main()
