

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement


class pdfConfig(ConfigElement):
    """ A pdfConfig ConfigElement.

    Args:
        default (str): The default action: allow, disallow, or sanitise.

    Key word arguments can be specified to change individual switch values:
    pdfConfig(default="allow", embedded_images="sanitise")
    """

    def __init__(self, default: str = "sanitise", attributes: dict = {}, **kwargs):
        self.name = self.__class__.__name__
        self.default = default
        self.attributes = attributes
        self.switches_module = switches.pdf
        self.default_switches = [
            self.switches_module.acroform(value=default),
            self.switches_module.actions_all(value=default),
            self.switches_module.digital_signatures(value=default),
            self.switches_module.embedded_files(value=default),
            self.switches_module.embedded_images(value=default),
            self.switches_module.external_hyperlinks(value=default),
            self.switches_module.internal_hyperlinks(value=default),
            self.switches_module.javascript(value=default),
            self.switches_module.metadata(value=default),
        ]

        super().__init__(
            name=self.name,
            default=self.default,
            attributes=self.attributes,
            switches_module=self.switches_module,
            default_switches=self.default_switches,
            config=kwargs
        )
