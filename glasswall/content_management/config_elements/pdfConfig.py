

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement


class pdfConfig(ConfigElement):
    """ A pdfConfig ConfigElement.

    Args:
        default (str): The default action: allow, disallow, or sanitise.

    Key word arguments can be specified to change individual switch values:
    pdfConfig(default="allow", embedded_images="sanitise")
    """

    def __init__(self, default: str = "sanitise", **kwargs):
        self.name = self.__class__.__name__
        self.default = default
        self.switches_module = switches.pdf
        self.default_switches = [
            self.switches_module.acroform,
            self.switches_module.actions_all,
            self.switches_module.digital_signatures,
            self.switches_module.embedded_files,
            self.switches_module.embedded_images,
            self.switches_module.external_hyperlinks,
            self.switches_module.internal_hyperlinks,
            self.switches_module.javascript,
            self.switches_module.metadata,
        ]

        super().__init__(
            name=self.name,
            default=self.default,
            switches_module=self.switches_module,
            default_switches=self.default_switches,
            config=kwargs
        )
