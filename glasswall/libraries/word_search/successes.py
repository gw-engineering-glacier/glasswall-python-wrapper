# Statuses from sdk.word.search\src\glasswall.word.search\code\common\common.def.h


from glasswall.libraries.word_search.classes import WordSearchSuccess


# Differs from gw2ret_ok in sdk.editor, but preserved for backwards compatability.
class Success(WordSearchSuccess):
    """ WordSearch success code 1. """
    pass


success_codes = {
    1: Success,
}
