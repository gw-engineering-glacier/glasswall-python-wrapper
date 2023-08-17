

import os
import pathlib
import unittest

import glasswall
from glasswall import utils


class TestCompareNewListFilePaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use root of glasswall directory to test
        cls.test_directory = glasswall._ROOT

    @staticmethod
    def list_file_paths_old(directory: str, recursive: bool = True, absolute: bool = True, followlinks: bool = True):
        """ Returns a list of paths to files in a directory.

        Args:
            directory (str): The directory to list files from.
            recursive (bool, optional): Default True. Include subdirectories.
            absolute (bool, optional): Default True. Return paths as absolute paths. If False, returns relative paths.
            followlinks (bool, optional): Default True. Follow symbolic links if True.

        Returns:
            files (list): A list of file paths.
        """
        if not os.path.isdir(directory):
            raise NotADirectoryError(directory)

        if recursive:
            files = [
                os.path.normpath(os.path.join(root, file_))
                for root, dirs, files in os.walk(directory)
                for file_ in files
            ]
        else:
            files = [
                os.path.normpath(os.path.join(directory, file_))
                for file_ in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, file_))
            ]

        if followlinks:
            files = [
                str(pathlib.Path(file_).resolve())
                for file_ in files
            ]

        if absolute:
            files = [
                os.path.abspath(file_)
                for file_ in files
            ]
        else:
            files = [
                os.path.relpath(file_, directory)
                for file_ in files
            ]

        # Remove duplicate file paths (symlinks of same files or other symlinks), and sort
        files = sorted(set(files))

        return files

    def test_absolute_recursive_followlinks(self):
        result_new = utils.list_file_paths(self.test_directory, absolute=True, recursive=True, followlinks=True)
        result_old = self.list_file_paths_old(self.test_directory, absolute=True, recursive=True, followlinks=True)
        self.assertEqual(result_new, result_old)

    def test_absolute_recursive_nofollowlinks(self):
        result_new = utils.list_file_paths(self.test_directory, absolute=True, recursive=True, followlinks=False)
        result_old = self.list_file_paths_old(self.test_directory, absolute=True, recursive=True, followlinks=False)
        self.assertEqual(result_new, result_old)

    def test_absolute_nonrecursive_followlinks(self):
        result_new = utils.list_file_paths(self.test_directory, absolute=True, recursive=False, followlinks=True)
        result_old = self.list_file_paths_old(self.test_directory, absolute=True, recursive=False, followlinks=True)
        self.assertEqual(result_new, result_old)

    def test_absolute_nonrecursive_nofollowlinks(self):
        result_new = utils.list_file_paths(self.test_directory, absolute=True, recursive=False, followlinks=False)
        result_old = self.list_file_paths_old(self.test_directory, absolute=True, recursive=False, followlinks=False)
        self.assertEqual(result_new, result_old)

    def test_relative_recursive_followlinks(self):
        result_new = utils.list_file_paths(self.test_directory, absolute=False, recursive=True, followlinks=True)
        result_old = self.list_file_paths_old(self.test_directory, absolute=False, recursive=True, followlinks=True)
        self.assertEqual(result_new, result_old)

    def test_relative_recursive_nofollowlinks(self):
        result_new = utils.list_file_paths(self.test_directory, absolute=False, recursive=True, followlinks=False)
        result_old = self.list_file_paths_old(self.test_directory, absolute=False, recursive=True, followlinks=False)
        self.assertEqual(result_new, result_old)

    def test_relative_nonrecursive_followlinks(self):
        result_new = utils.list_file_paths(self.test_directory, absolute=False, recursive=False, followlinks=True)
        result_old = self.list_file_paths_old(self.test_directory, absolute=False, recursive=False, followlinks=True)
        self.assertEqual(result_new, result_old)

    def test_relative_nonrecursive_nofollowlinks(self):
        result_new = utils.list_file_paths(self.test_directory, absolute=False, recursive=False, followlinks=False)
        result_old = self.list_file_paths_old(self.test_directory, absolute=False, recursive=False, followlinks=False)
        self.assertEqual(result_new, result_old)


if __name__ == '__main__':
    unittest.main()
