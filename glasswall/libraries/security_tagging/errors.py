
from glasswall.libraries.security_tagging.classes import SecurityTaggingError


class UnknownErrorCode(SecurityTaggingError):
    """ Unknown error code. """
    pass


# TODO expand, pending security tagging status code enhancements
class GeneralFail(SecurityTaggingError):
    """ SecurityTagging error code 0. """
    pass


error_codes = {
    0: GeneralFail,
}
