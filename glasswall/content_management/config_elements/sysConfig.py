

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement


class sysConfig(ConfigElement):
    """ A sysConfig ConfigElement.

    Key word arguments can be specified to change individual switch values:
    sysConfig(interchange_type="sisl",interchange_pretty="true",)
    """

    def __init__(self, attributes={}, **kwargs):
        self.name = self.__class__.__name__
        self.attributes = attributes

        self.switches_module = switches.sys
        self.default_switches = [
            self.switches_module.interchange_type(value="sisl"),
            self.switches_module.interchange_pretty(value="false"),
            self.switches_module.interchange_best_compression(value="false"),
            self.switches_module.export_embedded_images(value="true"),
            self.switches_module.run_mode(value="enablerebuild")
        ]

        super().__init__(
            name=self.name,
            attributes=self.attributes,
            switches_module=self.switches_module,
            default_switches=self.default_switches,
            config=kwargs
        )
