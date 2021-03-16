

import ctypes as ct
import hashlib
import io
import json
import logging
import os
import pathlib
import re
import tempfile
from distutils.version import LooseVersion
from typing import Iterable, Union

from lxml import etree

import glasswall

log = logging.getLogger("glasswall")


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


def list_file_paths(directory: str, recursive: bool = True, absolute: bool = True):
    """ Returns a list of paths to files in a directory.

    Args:
        directory (str): The directory to list files from.
        recursive (bool, optional): Default True. Include subdirectories.
        absolute (bool, optional): Default True. Return paths as absolute paths. If False, returns relative paths.

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


def _max_version_in_path(path: pathlib.Path):
    """ Helper function for get_library, returns the highest LooseVersion.version in a path.parts, avoiding int to str comparisons. """
    # prioritise path parts starting with a digit 0-9
    starts_digit = [p for p in path.parts if p.startswith(tuple(map(str, range(10))))]
    if starts_digit:
        part = max(starts_digit, key=lambda x: LooseVersion(x).version)

    # if no path parts start with a digit, don't try to sort it
    else:
        part = "0"

    return LooseVersion(part).version


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
    library = as_snake_case(library)
    library_file_name = glasswall.libraries.os_info[glasswall._OPERATING_SYSTEM][library]["file_name"]

    p = pathlib.Path(directory)
    matching_files = list(p.rglob(library_file_name))

    if not matching_files:
        raise FileNotFoundError(f'Could not find file: "{library_file_name}" under directory: "{directory}"')

    library_file_path = str(max(matching_files, key=os.path.getctime).resolve())

    if len(matching_files) > 1:
        # warn that multiple libraries found, list library paths if there are <= 5
        if len(matching_files) <= 5:
            log.warning(f"Found {len(matching_files)} {library} libraries, but expected only one:\n{chr(10).join(str(item) for item in matching_files)}\nLatest library: {library_file_path}")
        else:
            log.warning(f"Found {len(matching_files)} {library} libraries, but expected only one.\nLatest library: {library_file_path}")

    return library_file_path


def get_libraries(directory: str, ignore_errors: bool = False):
    """ Recursively calls get_library on each library from glasswall.libraries.os_info on the given directory.

    Args:
        directory (str): The directory to search from.
        ignore_errors (bool, optional): Default False, prevents get_library raising FileNotFoundError when True.

    Returns:
        libraries (dict[str, str]): A dictionary of library names and their absolute file paths.
    """
    libraries = {}

    for library_name in glasswall.libraries.os_info[glasswall._OPERATING_SYSTEM].keys():
        try:
            libraries[library_name] = get_library(library_name, directory)
        except FileNotFoundError:
            if ignore_errors is True:
                continue
            raise

    return libraries


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


# NOTE typehint as string due to no "from __future__ import annotations" support on python 3.6 on ubuntu-16.04 / centos7
def validate_xml(xml: Union[str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.Policy"]):
    """ Attempts to parse the xml provided, returning the xml as string. Raises ValueError if the xml cannot be parsed.

    Args:
        xml (Union[str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.Policy]): The xml string, or file path, bytes, or ContentManagementPolicy instance to parse.

    Returns:
        xml_string (str): A string representation of the xml.

    Raises:
        ValueError: if the xml cannot be parsed.
        TypeError: if the type of arg "xml" is invalid
    """
    try:
        # Get tree from file
        if isinstance(xml, str) and os.path.isfile(xml):
            tree = etree.parse(xml)

        # Get tree from xml string
        elif isinstance(xml, str):
            xml = xml.encode("utf-8")
            tree = etree.fromstring(xml)

        # Get tree from bytes, bytearray, io.BytesIO
        elif isinstance(xml, (bytes, bytearray, io.BytesIO)):
            # Convert bytes, bytearray to io.BytesIO
            if isinstance(xml, (bytes, bytearray)):
                xml = as_io_BytesIO(xml)
            tree = etree.parse(xml)

        # Get tree from ContentManagementPolicy instance
        elif isinstance(xml, glasswall.content_management.policies.Policy):
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


##################################################
""" TODO gated-check-in functions, to be moved """
##################################################


def delete_empty_subdirectories(directory: str):
    """ Deletes all empty subdirectories of a given directory.

    Args:
        directory (str): The directory to delete subdirectories from.

    Returns:
        None
    """
    for root, dirs, _ in os.walk(directory, topdown=False):
        for dir_ in dirs:
            try:
                # Delete if empty
                os.rmdir(os.path.realpath(os.path.join(root, dir_)))
            except OSError:
                pass


def delete_directory(directory: str, keep_folder: bool = False):
    """ Delete a directory and its contents.

    Args:
        directory (str): The directory path.
        keep_folder (bool, optional): Default False. If False, only delete contents.
    """
    if os.path.isdir(directory):
        # Delete all files in directory
        for file_ in list_file_paths(directory):
            os.remove(file_)

        # Delete all empty subdirectories
        delete_empty_subdirectories(directory)

        # Delete the directory
        if keep_folder is False:
            os.rmdir(directory)


def crossplatform_path(path: str):
    """ Makes a path cross-platform and suitable for comparison. Calls os.normpath and then replaces all "\\" with "/"

    Args:
        path (str): The path to simplify.

    Returns:
        path (str): The simplified path.
    """
    return os.path.normpath(path).replace("\\", "/")


def _md5_chunked(file_: bytes, chunk_size: int):
    """ Returns an md5 read in chunk_size bytes. There are 1_048_576 bytes in 1 MB.

    Args:
        file_ (bytes): The file bytes.
        chunk_size (int): The size of chunks to read from file_.

    Returns:
        md5 (hashlib.md5()): A hashlib.md5() object
    """
    md5 = hashlib.md5()
    while True:
        data = file_.read(chunk_size)
        if not data:
            break
        md5.update(data)

    return md5


def get_md5(file_: Union[bytes, str], chunk_size: int = 67_108_864, from_string: bool = False):
    """ Returns the md5 hash of the given file.

    Args:
        file_ (Union[bytes, str]): The file bytes or file path.
        chunk_size (int): The size of chunks to read from file_.
        from_string (bool): Generate md5 from string instead of assuming string is a file path.

    Returns:
        md5 (str): A string representing an md5 hash.
    """
    if not isinstance(file_, (bytes, str,)):
        raise TypeError(f"file_ must be one of type: {(bytes, str,)} and not {type(file_)}")
    elif isinstance(file_, bytes):
        md5 = hashlib.md5()
        md5.update(file_)
    elif isinstance(file_, str):
        if from_string:
            md5 = hashlib.md5()
            md5.update(file_.encode())
        else:
            with open(file_, "rb") as f:
                md5 = _md5_chunked(f, chunk_size)

    return md5.hexdigest()


def get_md5_directory(directory: str, **kwargs):
    """ Calls get_md5 on the contents of a directory and all subdirectories recursively. """
    return {
        file_path: get_md5(file_path, **kwargs)
        for file_path in list_file_paths(directory)
    }


def lxml_elements_equal(e1: etree.Element, e2: etree.Element):
    """ Returns True if lxml Elements e1 and e2 are equal, else False.
    Args:
        e1 (etree.Element): First lxml Element
        e2 (etree.Element): Second lxml Element

    Returns:
        bool
    """
    if any([
        e1.tag != e2.tag,
        e1.text != e2.text,
        e1.tail != e2.tail,
        e1.attrib != e2.attrib,
        len(e1) != len(e2)
    ]):
        return False
    return all(lxml_elements_equal(c1, c2) for c1, c2 in zip(e1, e2))


# TODO unused, but may be repurposed later
def get_sanitisation_item_technical_description(xml: Union[str, bytes, bytearray, io.BytesIO]):
    """ Returns a list of technical description strings found in an analysis .xml

    Args:
        xml (Union[str, bytes, bytearray, io.BytesIO]): The xml string, or file path, or bytes.

    Returns:
        technical_descriptions (list): A list of technical description strings from within the XML file.
    """
    # Convert xml to string
    xml_string = validate_xml(xml)

    # Get root
    root = etree.fromstring(xml_string.encode())

    technical_descriptions = [
        sanitisation_item.find("gw:TechnicalDescription", glasswall.config.xml.namespaces).text
        for sanitisation_item in root.findall(".//gw:SanitisationItem", glasswall.config.xml.namespaces)
    ]

    return technical_descriptions


def create_determine_file_type_dict(library, input_directory: str):
    """ Creates a dictionary of file paths and their corresponding int and str file types.

    Args:
        library (Union[glasswall.Editor, glasswall.Rebuild]): An instance of a Glasswall library.
        input_directory (str): The input directory containing files to run determine_file_type on.

    Returns:
        dft_dict (dict): A dictionary of file paths and their corresponding int and str file types.
    """
    # Construct dictionary of file paths, their file type as int, and their file type as str
    dft_dict = {
        crossplatform_path(os.path.relpath(file_path, input_directory)): {
            "int": library.determine_file_type(file_path),
            "str": library.determine_file_type(file_path, as_string=True)
        }
        for file_path in list_file_paths(input_directory)
    }

    return dft_dict


def save_dictionary_as_json(dictionary: dict, output_file: str):
    """ Writes the determine file type dictionary to the output path as JSON.

    Args:
        dictionary (dict): A dictionary.
        output_file (str): The output file path where the dictionary will be written as JSON.

    Returns:
        None
    """
    if not os.path.isfile(output_file):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write(json.dumps(dictionary, indent=4))


def load_json_as_dictionary(json_path: str):
    """ Loads JSON from json_path, returning a dictionary.

    Args:
        json_path (str): The JSON file to return as a dictionary.

    Returns:
        dictionary (dict): A dictionary containing the JSON file data.
    """
    with open(json_path) as f:
        return json.load(f)


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

        # Create temp directory if it does not exist
        os.makedirs(os.path.dirname(self.temp_file), exist_ok=True)

    def __enter__(self):
        return self.temp_file

    def __exit__(self, type, value, traceback):
        if self.delete:
            if os.path.isfile(self.temp_file):
                os.remove(self.temp_file)


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
            self.temp_directory = os.path.join(glasswall._TEMPDIR, next(tempfile._get_candidate_names()), "")

        # Create temp directory
        os.makedirs(self.temp_directory, exist_ok=True)

    def __enter__(self):
        return self.temp_directory

    def __exit__(self, type, value, traceback):
        if self.delete:
            # Delete temp directory and all of its contents
            if os.path.isdir(self.temp_directory):
                delete_directory(self.temp_directory)


def flatten_list(list_: Iterable):
    """ Returns a flattened list. [[1, 2], ["3"], (4, 5,), [6]] --> [1, 2, "3", 4, 5, 6] """
    return [
        item
        for sublist in list_
        for item in sublist
    ]


def get_valgrind_leak_summary(file_path: str):
    """ Returns the LEAK SUMMARY lines from a Valgrind log file as a dictionary.

    Args:
        file_path (str): Path to the Valgrind .log file

    Returns:
        leak_summary (dict): A dictionary of the Valgrind leak summary.

    Example return:

    {
        "definitely lost": {"bytes": 0, "blocks": 0},
        "indirectly lost": {"bytes": 0, "blocks": 0},
        "possibly lost": {"bytes": 6776, "blocks": 12},
        "still reachable": {"bytes": 486982, "blocks": 198},
        "suppressed": {"bytes": 0, "blocks": 0},
    }
    """
    leak_summary = {}
    pattern = re.compile(r"(.+): (\d+) bytes in (\d+) blocks")
    capture_lines = False
    with open(file_path) as f:
        for line in f:
            # Start capturing lines when "LEAK SUMMARY:" is found
            if "LEAK SUMMARY:" in line:
                capture_lines = True
            if capture_lines:
                # Format line
                line = line.partition("== ")[-1].lstrip().rstrip().replace(",", "")

                # Break for loop at the first empty line
                if not line:
                    break

                match = re.match(pattern, line)
                if not match:
                    log.warning(f"Unable to find match in Valgrind log line:\n{line}")
                    continue

                key, bytes_, blocks = re.match(pattern, line).groups()

                # Add this line to leak_summary
                leak_summary[key] = {
                    "bytes": int(bytes_),
                    "blocks": int(blocks),
                }

    return leak_summary
