

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement


class tiffConfig(ConfigElement):
    """ A tiffConfig ConfigElement.

    Args:
        default (str): The default action: allow, disallow, or sanitise.

    Key word arguments can be specified to change individual switch values:
    tiffConfig(geotiff="sanitise")
    """

    def __init__(self, default: str = "sanitise", **kwargs):
        self.name = self.__class__.__name__
        self.default = default
        self.switches_module = switches.tiff
        self.default_switches = [
            self.switches_module.geotiff,
        ]

        super().__init__(
            name=self.name,
            default=self.default,
            switches_module=self.switches_module,
            default_switches=self.default_switches,
            config=kwargs
        )
