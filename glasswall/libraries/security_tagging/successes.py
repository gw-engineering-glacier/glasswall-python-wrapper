

from glasswall.libraries.security_tagging.classes import SecurityTaggingSuccess


# TODO expand, pending security tagging status code enhancements
class OK(SecurityTaggingSuccess):
    """ SecurityTagging success code 1. """
    pass


success_codes = {
    1: OK,
}
