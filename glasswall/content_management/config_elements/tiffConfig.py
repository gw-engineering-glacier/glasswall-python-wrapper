

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
        self.switches = [
            switches.tiff.geotiff(value=kwargs.get("geotiff", default)),
        ]
        super().__init__(name=self.name, switches=self.switches)
