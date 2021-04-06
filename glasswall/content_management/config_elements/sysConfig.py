

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement
from glasswall.content_management.switches import Switch


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

        self.name = self.__class__.__name__
        self.switches_module = switches.sys
        self.default_switches = [
            self.switches_module.interchange_type,
            self.switches_module.interchange_pretty,
        ]
        self.switches = []

        # Add default switches
        for switch in self.default_switches:
            self.add_switch(switch(value=switch.default))

        # Add customised switches provided in `kwargs`
        for name, value in kwargs.items():
            # If switch is in switches_module, add it to this config element
            if hasattr(self.switches_module, name):
                self.add_switch(
                    getattr(
                        self.switches_module,
                        name
                    )(value=value))

            # Otherwise, create a new Switch and add it
            else:
                self.add_switch(Switch(name=name, value=value))

        super().__init__(name=self.name, switches=self.switches)
