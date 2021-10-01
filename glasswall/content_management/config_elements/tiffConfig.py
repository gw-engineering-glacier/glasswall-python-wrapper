

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement


class tiffConfig(ConfigElement):
    """ A tiffConfig ConfigElement.

    Args:
        default (str): The default action: allow, disallow, or sanitise.

    Key word arguments can be specified to change individual switch values:
    tiffConfig(geotiff="sanitise")
    """

    def __init__(self, default: str = "sanitise", attributes={}, **kwargs):
        self.name = self.__class__.__name__
        self.default = default
        self.attributes = attributes
        self.switches_module = switches.tiff
        self.default_switches = [
            self.switches_module.geotiff(value=default),
        ]

        super().__init__(
            name=self.name,
            default=self.default,
            attributes=self.attributes,
            switches_module=self.switches_module,
            default_switches=self.default_switches,
            config=kwargs
        )
