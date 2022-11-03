

import ctypes as ct
import functools
import io
import os
import pathlib
import stat
import tempfile
import warnings
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

from lxml import etree

import glasswall
from glasswall.config.logging import log


def as_bytes(file_: Union[bytes, bytearray, io.BytesIO]):
    """ Returns file_ as bytes.

    Args:
        file_ (Union[bytes, bytearray, io.BytesIO]): The file

    Returns:
        bytes

    Raises:
        TypeError: If file_ is not an instance of: bytes, bytearray, io.BytesIO
    """
    if isinstance(file_, bytes):
        return file_
    elif isinstance(file_, bytearray):
        return bytes(file_)
    elif isinstance(file_, io.BytesIO):
        return file_.read()
    else:
        raise TypeError(file_)


def as_io_BytesIO(file_: Union[bytes, bytearray]):
    """ Returns file_ as io.BytesIO object.

    Args:
        file_ (Union[bytes, bytearray]): The bytes or bytearray of the file

    Returns:
        io.BytesIO object

    Raises:
        TypeError: If file_ is not an instance of: bytes, bytearray, io.BytesIO
    """
    if isinstance(file_, bytes):
        return io.BytesIO(file_)
    elif isinstance(file_, bytearray):
        return io.BytesIO(bytes(file_))
    elif isinstance(file_, io.BytesIO):
        return file_
    else:
        raise TypeError(file_)


def as_snake_case(string):
    return ''.join(
        [
            '_' + char.lower()
            if char.isupper() else char
            for char in string
        ]
    ).lstrip('_')


def as_title(string):
    return ''.join(
        word.title()
        for word in string.split("_")
    )


def buffer_to_bytes(buffer: ct.c_void_p, buffer_length: ct.c_size_t):
    """ Convert ctypes buffer and buffer_length to bytes.

    Args:
        buffer (ct.c_void_p()): The file buffer.
        buffer_length (ct.c_size_t()): The file buffer length.

    Returns:
        bytes (bytes): The file as bytes.
    """

    file_buffer = (ct.c_byte * buffer_length.value)()
    ct.memmove(file_buffer, buffer.value, buffer_length.value)

    return bytes(file_buffer)


class CwdHandler:
    """ Changes the current working directory to new_cwd on __enter__, and back to previous cwd on __exit__.

    Args:
        new_cwd (str): The new current working directory to temporarily change to.
    """

    def __init__(self, new_cwd: str):
        self.new_cwd = new_cwd if os.path.isdir(new_cwd) else os.path.dirname(new_cwd)
        self.old_cwd = os.getcwd()

    def __enter__(self):
        os.chdir(self.new_cwd)

    def __exit__(self, type, value, traceback):
        os.chdir(self.old_cwd)


def delete_directory(directory: str, keep_folder: bool = False):
    """ Delete a directory and its contents.

    Args:
        directory (str): The directory path.
        keep_folder (bool, optional): Default False. If False, only delete contents.
    """
    if os.path.isdir(directory):
        # Delete all files in directory
        for file_ in list_file_paths(directory, followlinks=False):
            os.remove(file_)

        # Delete all empty subdirectories
        delete_empty_subdirectories(directory)

        # Delete the directory
        if keep_folder is False:
            os.rmdir(directory)


def delete_empty_subdirectories(directory: str):
    """ Deletes all empty subdirectories of a given directory.

    Args:
        directory (str): The directory to delete subdirectories from.

    Returns:
        None
    """

    for root, dirs, _ in os.walk(directory, topdown=False):
        for dir_ in dirs:
            absolute_path = os.path.join(root, dir_)
            try:
                os.rmdir(absolute_path)
            except PermissionError:
                # directory might be read-only
                try:
                    os.chmod(absolute_path, stat.S_IWRITE)
                except Exception:
                    log.warning(f"PermissionError while attempting to delete {absolute_path}. Attempted chmod but failed.")
                try:
                    os.rmdir(absolute_path)
                except OSError:
                    # cannot be deleted
                    pass
            except OSError:
                # not empty, don't delete
                pass


def flatten_list(list_: Iterable):
    """ Returns a flattened list. [[1, 2], ["3"], (4, 5,), [6]] --> [1, 2, "3", 4, 5, 6] """
    return [
        item
        for sublist in list_
        for item in sublist
    ]


def get_file_type(file_path: str):
    """ Returns the filetype of a file. "data/files/splat.zip" -> "zip" """
    return os.path.splitext(file_path)[-1].replace(".", "")


def get_libraries(directory: str, library_names: Optional[List[str]] = None, ignore_errors: bool = False):
    """ Recursively calls get_library on each library from glasswall.libraries.os_info on the given directory.

    Args:
        directory (str): The directory to search from.
        library_names (List[str], optional): List of libraries to return, if None iterates all libraries found in glasswall.libraries.os_info
        ignore_errors (bool, optional): Default False, prevents get_library raising FileNotFoundError when True.

    Returns:
        libraries (dict[str, str]): A dictionary of library names and their absolute file paths.
    """
    libraries = {}

    if not library_names:
        library_names = glasswall.libraries.os_info[glasswall._OPERATING_SYSTEM].keys()

    for library_name in library_names:
        try:
            libraries[library_name] = get_library(library_name, directory)
        except FileNotFoundError:
            if ignore_errors is True:
                continue
            raise

    return libraries


def get_library(library: str, directory: str):
    """ Returns a path to the specified library found from the current directory or any subdirectory. If multiple libraries exist, returns the file with the latest modified time.

    Args:
        library (str): The library to search for, ie: "rebuild", "word_search"
        directory (str): The directory to search from.

    Returns:
        library_file_path (str): The absolute file path to the library.

    Raises:
        KeyError: Unsupported OS or library name was not found in glasswall.libraries.os_info.
        FileNotFoundError: Library was not found.
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(directory)

    library = as_snake_case(library)
    library_file_names = glasswall.libraries.os_info[glasswall._OPERATING_SYSTEM][library]["file_name"]

    if isinstance(library_file_names, str):
        library_file_names = [library_file_names]

    matches = []
    for alias in library_file_names:
        p = pathlib.Path(directory)
        alias_matches = list(p.rglob(alias))
        matches.extend(alias_matches)

    if matches:
        latest_library = str(max(matches, key=os.path.getctime).resolve())
        if len(matches) > 1:
            # warn that multiple libraries found, list library paths if there are <= 5
            if len(matches) <= 5:
                log.warning(f"Found {len(matches)} {library} libraries, but expected only one:\n{chr(10).join(str(item) for item in matches)}\nLatest library: {latest_library}")
            else:
                log.warning(f"Found {len(matches)} {library} libraries, but expected only one.\nLatest library: {latest_library}")

        # Return library with latest change time
        return latest_library

    # exhausted, not found
    raise FileNotFoundError(f'Could not find any files: "{library_file_names}" under directory: "{directory}"')


def list_file_paths(directory: str, recursive: bool = True, absolute: bool = True, followlinks: bool = True):
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


def list_subdirectory_paths(directory: str, recursive: bool = False, absolute: bool = True):
    """ Returns a list of paths to subdirectories in a directory.

    Args:
        directory (str): The directory to list subdirectories from.
        recursive (bool, optional): Default False. Include subdirectories of subdirectories.
        absolute (bool, optional): Default True. Return paths as absolute paths. If False, returns relative paths.

    Returns:
        subdirectories (list): A list of subdirectory paths.
    """
    subdirectories = [f.path for f in os.scandir(directory) if f.is_dir()]

    if recursive:
        for subdirectory in subdirectories:
            subdirectories.extend(list_subdirectory_paths(subdirectory, recursive=True))

    if absolute:
        subdirectories = [os.path.abspath(path) for path in subdirectories]
    else:
        subdirectories = [os.path.relpath(path, directory) for path in subdirectories]

    return subdirectories


def load_dependencies(dependencies: list, ignore_errors: bool = False):
    """ Calls ctypes.cdll.LoadLibrary on each file path in `dependencies`.

    Args:
        dependencies (list): A list of absolute file paths of library dependencies.
        ignore_errors (bool, optional): Default False, avoid raising exceptions from ct.cdll.LoadLibrary if ignore_errors is True.

    Returns:
        missing_dependencies (list): A list of missing dependencies, or an empty list.
    """
    missing_dependencies = [dependency for dependency in dependencies if not os.path.isfile(dependency)]

    for dependency in dependencies:
        # Try to load dependencies that exist
        if dependency not in missing_dependencies:
            try:
                ct.cdll.LoadLibrary(dependency)
            except Exception:
                if ignore_errors:
                    pass
                else:
                    raise

    return missing_dependencies


class TempDirectoryPath:
    """ Gives a path to a uniquely named temporary directory that does not currently exist on __enter__, deletes the directory if it exists on __exit__.

    Args:
        delete (bool, optional): Default True. Delete the temporary directory on __exit__
    """

    def __init__(self, delete: bool = True):
        # Validate args
        if not isinstance(delete, bool):
            raise TypeError(delete)

        self.temp_directory = None
        self.delete = delete

        while self.temp_directory is None or os.path.isdir(self.temp_directory):
            self.temp_directory = os.path.join(glasswall._TEMPDIR, next(tempfile._get_candidate_names()))

        # Normalize
        self.temp_directory = str(pathlib.Path(self.temp_directory).resolve())

        # Create temp directory
        os.makedirs(self.temp_directory, exist_ok=True)

    def __enter__(self):
        return self.temp_directory

    def __exit__(self, type, value, traceback):
        if self.delete:
            # Delete temp directory and all of its contents
            if os.path.isdir(self.temp_directory):
                delete_directory(self.temp_directory)


class TempFilePath:
    """ Gives a path to a uniquely named temporary file that does not currently exist on __enter__, deletes the file if it exists on __exit__.

    Args:
        directory (Union[str, None], optional): The directory to create a temporary file in.
        delete (bool, optional): Default True. Delete the temporary file on on __exit__
    """

    def __init__(self, directory: Union[str, None] = None, delete: bool = True):
        # Validate args
        if not isinstance(directory, (str, type(None))):
            raise TypeError(directory)
        if isinstance(directory, str) and not os.path.isdir(directory):
            raise NotADirectoryError(directory)
        if not isinstance(delete, bool):
            raise TypeError(delete)

        self.temp_file = None
        self.directory = directory or tempfile.gettempdir()
        self.delete = delete

        while self.temp_file is None or os.path.isfile(self.temp_file):
            self.temp_file = os.path.join(self.directory, next(tempfile._get_candidate_names()))

        # Normalize
        self.temp_file = str(pathlib.Path(self.temp_file).resolve())

        # Create temp directory if it does not exist
        os.makedirs(os.path.dirname(self.temp_file), exist_ok=True)

    def __enter__(self):
        return self.temp_file

    def __exit__(self, type, value, traceback):
        if self.delete:
            if os.path.isfile(self.temp_file):
                os.remove(self.temp_file)


# NOTE typehint as string due to no "from __future__ import annotations" support on python 3.6 on ubuntu-16.04 / centos7
def validate_xml(xml: Union[str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"]):
    """ Attempts to parse the xml provided, returning the xml as string. Raises ValueError if the xml cannot be parsed.

    Args:
        xml (Union[str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy]): The xml string, or file path, bytes, or ContentManagementPolicy instance to parse.

    Returns:
        xml_string (str): A string representation of the xml.

    Raises:
        ValueError: if the xml cannot be parsed.
        TypeError: if the type of arg "xml" is invalid
    """
    try:
        # Get tree from file/str
        if isinstance(xml, str):
            try:
                is_file = os.path.isfile(os.path.abspath(xml))
            except Exception:
                is_file = False

            if is_file:
                tree = etree.parse(xml)
            else:
                xml = xml.encode("utf-8")
                tree = etree.fromstring(xml)

        # Get tree from bytes, bytearray, io.BytesIO
        elif isinstance(xml, (bytes, bytearray, io.BytesIO)):
            # Convert bytes, bytearray to io.BytesIO
            if isinstance(xml, (bytes, bytearray)):
                xml = as_io_BytesIO(xml)
            tree = etree.parse(xml)

        # Get tree from ContentManagementPolicy instance
        elif isinstance(xml, glasswall.content_management.policies.policy.Policy):
            xml = xml.text.encode("utf-8")
            tree = etree.fromstring(xml)

        else:
            raise TypeError(xml)

    except etree.XMLSyntaxError:
        raise ValueError(xml)

    # # convert tree to string and include xml declaration header utf8
    etree.indent(tree, space=" " * 4)
    xml_string = etree.tostring(tree, encoding="utf-8", xml_declaration=True, pretty_print=True).decode()

    return xml_string


def xml_as_dict(xml):
    """ Converts a simple single-level xml into a dictionary.

    Args:
        xml (Union[str, bytes, bytearray, io.BytesIO]): The xml string, or file path, or bytes to parse.

    Returns:
        dict_ (dict): A dictionary of element tag : text
    """
    # Convert xml to string
    xml_string = validate_xml(xml)

    # Get root
    root = etree.fromstring(xml_string.encode())

    dict_ = {
        element.tag: element.text
        for element in root
    }

    # Sort for ease of viewing logs
    dict_ = {k: v for k, v in sorted(dict_.items())}

    return dict_


def deprecated_alias(**aliases: str) -> Callable:
    """ Decorator for deprecated function and method arguments.

    Use as follows:

    @deprecated_alias(old_arg='new_arg')
    def myfunc(new_arg):
        ...

    https://stackoverflow.com/a/49802489
    """

    def deco(f: Callable):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            rename_kwargs(f.__name__, kwargs, aliases)
            return f(*args, **kwargs)

        return wrapper

    return deco


def rename_kwargs(func_name: str, kwargs: Dict[str, Any], aliases: Dict[str, str]):
    """ Helper function for deprecating function arguments.

    https://stackoverflow.com/a/49802489
    """
    for alias, new in aliases.items():
        if alias in kwargs:
            if new in kwargs:
                raise TypeError(
                    f"{func_name} received both {alias} and {new} as arguments!"
                    f" {alias} is deprecated, use {new} instead."
                )
            warnings.warn(
                message=(
                    f"`{alias}` is deprecated as an argument to `{func_name}`; use"
                    f" `{new}` instead."
                ),
                category=DeprecationWarning,
                stacklevel=3,
            )
            kwargs[new] = kwargs.pop(alias)
