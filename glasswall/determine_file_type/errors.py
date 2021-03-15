

from glasswall.determine_file_type.classes import FileTypeEnumError


class UnknownErrorCode(FileTypeEnumError):
    """ Unknown error code. """
    pass


# The default when we don't know or can't determine the file type.
class ft_unknown(FileTypeEnumError):
    integer = 0
    string = "unknown"


# Not related to filetypes, but these are required since they give information when something goes wrong.
class ft_fileIssues(FileTypeEnumError):
    integer = 1
    string = "fileIssues"


class ft_bufferIssues(FileTypeEnumError):
    integer = 2
    string = "bufferIssues"


class ft_internalIssues(FileTypeEnumError):
    integer = 3
    string = "internalIssues"


class ft_licenseExpired(FileTypeEnumError):
    integer = 4
    string = "licenseExpired"


class ft_passwordProtectedOpcFile(FileTypeEnumError):
    integer = 5
    string = "passwordProtectedOpcFile"


class ft_nullPointerArgument(FileTypeEnumError):
    integer = 6
    string = "nullPointerArgument"
