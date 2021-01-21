

import ctypes as ct
import os

import glasswall
from glasswall import utils


class Library:
    """ A Glasswall library. """

    def __init__(self, library_path: str):
        self.library_path = library_path

    def load_library(self, library_path: str):
        if not os.path.isfile(library_path):
            if os.path.isdir(library_path):
                library_path = utils.get_library(self.__class__.__name__, library_path)
            else:
                raise FileNotFoundError(library_path)

        self.library_path = library_path

        # Preload dependencies to avoid "OSError: ...: cannot open shared object file: No such file or directory"
        dependencies = [
            os.path.join(os.path.dirname(self.library_path), dependency)
            for dependency in glasswall.libraries.os_info[glasswall._OPERATING_SYSTEM][utils.as_snake_case(self.__class__.__name__)]["dependencies"]
        ]
        missing_dependencies = utils.load_dependencies(dependencies, ignore_errors=True)

        with utils.CwdHandler(new_cwd=self.library_path):
            try:
                # Try to load library
                return ct.cdll.LoadLibrary(self.library_path)
            except OSError as e:
                # If library fails to load and there are missing dependencies, list them
                if missing_dependencies:
                    raise FileNotFoundError(f"Unable to load {self.__class__.__name__}. Below dependencies are missing in directory: {os.path.dirname(self.library_path)}\n{', '.join(missing_dependencies)}") from e
                raise
