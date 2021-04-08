

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
        self.default = default
        self.switches_module = switches.word
        self.default_switches = [
            self.switches_module.dynamic_data_exchange,
            self.switches_module.embedded_files,
            self.switches_module.embedded_images,
            self.switches_module.external_hyperlinks,
            self.switches_module.internal_hyperlinks,
            self.switches_module.macros,
            self.switches_module.metadata,
            self.switches_module.review_comments,
        ]

        super().__init__(
            name=self.name,
            default=self.default,
            switches_module=self.switches_module,
            default_switches=self.default_switches,
            config=kwargs
        )
