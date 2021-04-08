

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement


class sysConfig(ConfigElement):
    """ A sysConfig ConfigElement.

    Key word arguments can be specified to change individual switch values:
    sysConfig(interchange_type="xml", interchange_pretty="false")
    """

    def __init__(self, **kwargs):
        self.name = self.__class__.__name__
        self.switches_module = switches.sys
        self.default_switches = [
            self.switches_module.interchange_type,
            self.switches_module.interchange_pretty,
        ]

        super().__init__(
            name=self.name,
            switches_module=self.switches_module,
            default_switches=self.default_switches,
            config=kwargs
        )
