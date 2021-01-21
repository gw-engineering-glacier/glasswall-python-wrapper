
from glasswall.libraries.word_search.classes import WordSearchError


class UnknownErrorCode(WordSearchError):
    """ Unknown error code. """
    pass


# Statuses from sdk.word.search\src\glasswall.word.search\code\common\common.def.h
class Fail(WordSearchError):
    """ WordSearch error code 0. """
    pass


error_codes = {
    0: Fail,
}
