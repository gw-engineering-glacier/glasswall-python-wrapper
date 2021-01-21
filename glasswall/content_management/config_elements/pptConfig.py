

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement


class pptConfig(ConfigElement):
    """ A pptConfig ConfigElement.

    Args:
        default (str): The default action: allow, disallow, or sanitise.

    Key word arguments can be specified to change individual switch values:
    pptConfig(default="allow", embedded_images="sanitise")
    """

    def __init__(self, default: str = "sanitise", **kwargs):
        self.name = self.__class__.__name__
        self.switches = [
            switches.ppt.embedded_files(value=kwargs.get("embedded_files", default)),
            switches.ppt.embedded_images(value=kwargs.get("embedded_images", default)),
            switches.ppt.external_hyperlinks(value=kwargs.get("external_hyperlinks", default)),
            switches.ppt.internal_hyperlinks(value=kwargs.get("internal_hyperlinks", default)),
            switches.ppt.macros(value=kwargs.get("macros", default)),
            switches.ppt.metadata(value=kwargs.get("metadata", default)),
            switches.ppt.review_comments(value=kwargs.get("review_comments", default)),
        ]
        super().__init__(name=self.name, switches=self.switches)
