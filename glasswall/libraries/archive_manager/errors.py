

from .classes import ArchiveManagerError


class UnknownErrorCode(ArchiveManagerError):
    """ Unknown error code. """
    pass


# Statuses from sdk.archive.manager\src\glasswall.archive\code\common\custom.types.h
class Fail(ArchiveManagerError):
    """ ArchiveManager error code 0. """
    pass


error_codes = {
    0: Fail,
}
