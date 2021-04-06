

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement
from glasswall.content_management.switches import Switch


class pdfConfig(ConfigElement):
    """ A pdfConfig ConfigElement.

    Args:
        default (str): The default action: allow, disallow, or sanitise.

    Key word arguments can be specified to change individual switch values:
    pdfConfig(default="allow", embedded_images="sanitise")
    """

    def __init__(self, default: str = "sanitise", **kwargs):
        self.name = self.__class__.__name__
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
        self.switches = []

        # Add default switches
        for switch in self.default_switches:
            self.add_switch(switch(value=default))

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
