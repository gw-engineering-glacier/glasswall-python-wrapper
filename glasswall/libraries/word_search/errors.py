# Statuses from sdk.word.search\src\glasswall.word.search\code\common\common.def.h


from glasswall.libraries.word_search.classes import WordSearchError


class UnknownErrorCode(WordSearchError):
    """ Unknown error code. """
    pass


# Differs from gw2ret_generalfail in sdk.editor, but preserved for backwards compatability.
class Fail(WordSearchError):
    """ WordSearch error code 0. """
    pass


class DisallowedItemFound(WordSearchError):
    """ WordSearch error code -1024. Item disallowed by policy found in file. """
    pass


class RequiredItemNotFound(WordSearchError):
    """ WordSearch error code -1025. Item required by policy not found in file. """
    pass


class IllegalActionRedact(WordSearchError):
    """ WordSearch error code -1026. Redact action specified but filetype doesn't support redaction. """
    pass


class IllegalActionRequire(WordSearchError):
    """ WordSearch error code -1027. Require action specified but filetype doesn't support redaction. """
    pass


class IllegalActionNoRequire(WordSearchError):
    """ WordSearch error code -1028. Require action not specified but filetype needs one. """
    pass


class FiletypeUnsupported(WordSearchError):
    """ WordSearch error code -1029. Filetype supported by Editor but not by Word Search. """
    pass


error_codes = {
    0: Fail,
    -1024: DisallowedItemFound,
    -1025: RequiredItemNotFound,
    -1026: IllegalActionRedact,
    -1027: IllegalActionRequire,
    -1028: IllegalActionNoRequire,
    -1029: FiletypeUnsupported,
}
