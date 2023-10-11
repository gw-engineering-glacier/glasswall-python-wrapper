

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


def iterate_directory_entries(directory: str, file_type: str = 'all', absolute: bool = True, recursive: bool = True, followlinks: bool = True, start_directory: str = None):
    """ Generate entries (files, directories, or both) in a given directory using os.scandir().

    Args:
        directory (str): The path to the directory whose entries are to be listed.
        file_type (str, optional): Type of entries to return.
            - 'all': Return both files and directories (default).
            - 'files': Return only files.
            - 'directories': Return only directories.
        absolute (bool, optional): Whether to return absolute paths (default) or relative paths.
        recursive (bool, optional): Whether to recurse into subdirectories (default is True).
        followlinks (bool, optional): Whether to follow symbolic links and yield entries from the target directory (default is True).
        start_directory (str, optional): The starting directory used to calculate relative paths (default is None).

    Yields:
        str: The full path of each file or directory found in the specified directory.

    Raises:
        ValueError: If an invalid 'file_type' value is provided.
        NotADirectoryError: If the directory does not exist.

    Example:
        directory = '/path/to/your/directory'

        # Iterate through all entries (files and directories) in the directory
        for entry in iterate_directory_entries(directory):
            print(entry)

        # Iterate through only file entries in the directory
        for file in iterate_directory_entries(directory, file_type='files'):
            print("File:", file)

        # Iterate through only directory entries in the directory
        for directory in iterate_directory_entries(directory, file_type='directories'):
            print("Directory:", directory)
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(directory)

    allowed_types = ['all', 'files', 'directories']

    # Check if the provided file_type is valid
    if file_type not in allowed_types:
        raise ValueError(f"Invalid file_type '{file_type}'. Allowed values are {', '.join(allowed_types)}.")

    # Convert the directory to an absolute path
    directory = os.path.abspath(directory)

    # Set the start_directory to the provided directory if not specified
    start_directory = start_directory or directory

    # Get the directory entries using os.scandir()
    for entry in os.scandir(directory):
        # If the entry is a directory
        if entry.is_dir(follow_symlinks=followlinks):
            # If recursive is True, traverse the subdirectory
            if recursive:
                yield from iterate_directory_entries(entry.path, file_type, absolute, recursive, followlinks, start_directory)

            # If the file_type is not "files", yield the directory entry
            if file_type != "files":
                if absolute:
                    yield entry.path
                else:
                    yield os.path.relpath(entry.path, start=start_directory)

        # If the entry is a file
        elif entry.is_file(follow_symlinks=followlinks):
            # If the file_type is not "directories", yield the file entry
            if file_type != "directories":
                if absolute:
                    yield entry.path
                else:
                    yield os.path.relpath(entry.path, start=start_directory)


def list_file_paths(directory: str, file_type: str = 'files', absolute: bool = True, recursive: bool = True, followlinks: bool = True) -> list:
    """ List all file paths in a given directory and its subdirectories.

    Args:
        directory (str): The path to the directory whose file paths are to be listed.
        file_type (str, optional): Type of entries to return.
            - 'all': Return both files and directories.
            - 'files': Return only files (default).
            - 'directories': Return only directories.
        absolute (bool, optional): Whether to return absolute paths (default is True).
        recursive (bool, optional): Whether to recurse into subdirectories (default is True).
        followlinks (bool, optional): Whether to follow symbolic links and list file paths from the target directory (default is True).

    Returns:
        list: A list of file paths found in the specified directory and its subdirectories.

    Example:
        directory = '/path/to/your/directory'
        file_paths = list_file_paths(directory)
        print(file_paths)
    """
    # Remove duplicate file paths (symlinks of same files or other symlinks), and sort
    return sorted(set(iterate_directory_entries(directory, file_type, absolute, recursive, followlinks)))


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


def deprecated_function(replacement_function):
    def decorator(f: Callable):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            warnings.warn(
                message=f"Call to deprecated method: '{f.__name__}'. Use '{replacement_function.__name__}' instead.",
                category=DeprecationWarning,
                stacklevel=3
            )
            return replacement_function(*args, **kwargs)

        return wrapper

    return decorator
