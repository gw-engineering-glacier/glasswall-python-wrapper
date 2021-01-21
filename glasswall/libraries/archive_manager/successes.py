

from .classes import ArchiveManagerSuccess


# Statuses from sdk.ArchiveManager\src\core.support\sdk.interface\gw2_returnstatus.h
class Success(ArchiveManagerSuccess):
    """ ArchiveManager success code 1. """
    pass


success_codes = {
    1: Success,
}
