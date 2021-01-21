

from glasswall.content_management.errors.policies import ContentManagementPolicyError


class ConfigElementNotFound(ContentManagementPolicyError):
    """ The Content Management Policy ConfigElement could not be found. """
    pass
