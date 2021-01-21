

from typing import Union

from glasswall.determine_file_type.classes import FileTypeEnum, FileTypeEnumError, FileTypeEnumSuccess

error_list = FileTypeEnumError.__subclasses__()
success_list = FileTypeEnumSuccess.__subclasses__()

int_str_map = {
    fte_class.integer: fte_class.string
    for fte_class in error_list + success_list
    if all(key in fte_class.__dict__.keys() for key in ["integer", "string"])
}

str_int_map = {
    fte_class.string: fte_class.integer
    for fte_class in error_list + success_list
    if all(key in fte_class.__dict__.keys() for key in ["integer", "string"])
}

int_class_map = {
    fte_class.integer: fte_class
    for fte_class in error_list + success_list
    if all(key in fte_class.__dict__.keys() for key in ["integer"])
}


def is_success(file_type: Union[int, str, FileTypeEnumError, FileTypeEnumSuccess]):
    """ Checks if a file type corresponds to a success.

    Args:
        file_type (Union[int, str, FileTypeEnumError, FileTypeEnumSuccess]): An enum int returned by Glasswall, str representation of file type, or subclass of FileTypeEnum.

    Returns:
        bool: Returns True if file_type corresponds to a successful file type, else False.
    """
    if isinstance(file_type, int):
        return file_type in [s.integer for s in success_list]
    elif isinstance(file_type, str):
        return file_type in [s.string for s in success_list]
    elif issubclass(file_type, FileTypeEnum):
        return issubclass(file_type, FileTypeEnumSuccess)
    else:
        raise TypeError(file_type)


def file_type_int_to_str(integer: int):
    """ Converts a file type enum int to a string.

    Args:
        integer (int): The enum int that Glasswall returns when ing a file type.

    Returns:
        Union[type(None), str]: The string representation of a file type, or None. """
    return int_str_map.get(integer, None)


def file_type_str_to_int(string: str):
    """ Converts a file type string to an enum int.

    Args:
        string (str): A string representation of a file type.

    Returns:
        Union[type(None), int]: The enum int that Glasswall returns when determining a file type, or None. """
    return str_int_map.get(string, None)
