

from glasswall.libraries.word_search.classes import WordSearchSuccess


# Statuses from sdk.word.search\src\glasswall.word.search\code\common\common.def.h
class Success(WordSearchSuccess):
    """ WordSearch success code 1. """
    pass


success_codes = {
    1: Success,
}
