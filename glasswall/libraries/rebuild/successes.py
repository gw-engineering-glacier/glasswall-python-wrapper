# Statuses from sdk.rebuild\src\code\dll.gwfile\dll.gwfilestatus.h


from glasswall.libraries.rebuild.classes import RebuildSuccess


class Success(RebuildSuccess):
    """ Rebuild success code 1. This value indicates the operation completed successfully. Any required Analysis or Protection was carried out and completed. """
    pass


success_codes = {
    1: Success,
}
