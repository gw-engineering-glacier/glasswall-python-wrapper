

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement


class wordConfig(ConfigElement):
    """ A wordConfig ConfigElement.

    Args:
        default (str): The default action: allow, disallow, or sanitise.

    Key word arguments can be specified to change individual switch values:
    wordConfig(default="allow", embedded_images="sanitise")
    """

    def __init__(self, default: str = "sanitise", **kwargs):
        self.name = self.__class__.__name__
        self.switches = [
            switches.word.dynamic_data_exchange(value=kwargs.get("dynamic_data_exchange", default)),
            switches.word.embedded_files(value=kwargs.get("embedded_files", default)),
            switches.word.embedded_images(value=kwargs.get("embedded_images", default)),
            switches.word.external_hyperlinks(value=kwargs.get("external_hyperlinks", default)),
            switches.word.internal_hyperlinks(value=kwargs.get("internal_hyperlinks", default)),
            switches.word.macros(value=kwargs.get("macros", default)),
            switches.word.metadata(value=kwargs.get("metadata", default)),
            switches.word.review_comments(value=kwargs.get("review_comments", default)),
        ]
        super().__init__(name=self.name, switches=self.switches)
