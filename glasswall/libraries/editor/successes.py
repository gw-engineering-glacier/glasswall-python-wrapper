

from glasswall.libraries.editor.classes import EditorSuccess


# Statuses from sdk.editor\src\core.support\sdk.interface\gw2_returnstatus.h
class OK(EditorSuccess):
    """ Editor success code 0. """
    pass


class OKWithCleaning(EditorSuccess):
    """ Editor success code 1. """
    pass


success_codes = {
    0: OK,
    1: OKWithCleaning,
}
