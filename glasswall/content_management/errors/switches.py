

from glasswall.content_management.errors.policies import ContentManagementPolicyError


class SwitchNotFound(ContentManagementPolicyError):
    """ The Content Management Policy Switch could not be found. """
    pass


class RestrictedValue(ContentManagementPolicyError):
    """ The Content Management Policy Switch has an unexpected value. """
    pass
