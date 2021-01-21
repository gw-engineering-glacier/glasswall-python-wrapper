

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement


class sysConfig(ConfigElement):
    """ A sysConfig ConfigElement.

    Key word arguments can be specified to change individual switch values:
    sysConfig(interchange_type="xml", interchange_pretty="false")
    """

    def __init__(self, **kwargs):
        self.name = self.__class__.__name__
        self.switches = [
            switches.sys.interchange_type(value=kwargs.get("interchange_type", "sisl")),
            switches.sys.interchange_pretty(value=kwargs.get("interchange_pretty", "false")),
        ]
        super().__init__(name=self.name, switches=self.switches)
