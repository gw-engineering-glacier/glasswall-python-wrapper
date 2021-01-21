

class FileTypeEnum:
    """ Base class for all file type enumerations. """
    pass


class FileTypeEnumError(FileTypeEnum, Exception):
    """ Enumerations that correspond to an error. """
    pass


class FileTypeEnumSuccess(FileTypeEnum):
    """ Enumerations that correspond to a file type. """
    pass
