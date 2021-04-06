

from typing import Union

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement
from glasswall.content_management.switches import Switch


class archiveConfig(ConfigElement):
    """ An archiveConfig ConfigElement.

    Args:
        default (str): The default action: no_action, discard, or process.

    Key word arguments can be specified to change individual switch values:
    archiveConfig(default="no_action", jpeg="discard", pdf="process")
    """

    def __init__(self, default: str = "process", attributes: Union[dict, type(None)] = None, **kwargs):
        self.name = self.__class__.__name__
        self.attributes = attributes or {}
        self.attributes = {
            **{
                "defaultCompression": kwargs.get("@defaultCompression", "zip"),
                "libVersion": kwargs.get("@libVersion", "core2"),
                "recursionDepth": kwargs.get("@recursionDepth", "2")
            },
            **self.attributes,
        }
        self.switches_module = switches.archive
        self.default_switches = [
            self.switches_module.bmp,
            self.switches_module.doc,
            self.switches_module.docx,
            self.switches_module.elf,
            self.switches_module.emf,
            self.switches_module.gif,
            self.switches_module.jpeg,
            self.switches_module.mp3,
            self.switches_module.mp4,
            self.switches_module.mpg,
            self.switches_module.o,
            self.switches_module.pdf,
            self.switches_module.pe,
            self.switches_module.png,
            self.switches_module.ppt,
            self.switches_module.pptx,
            self.switches_module.tiff,
            self.switches_module.txt,
            self.switches_module.wav,
            self.switches_module.wmf,
            self.switches_module.xls,
            self.switches_module.xlsx,
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

        super().__init__(name=self.name, switches=self.switches, attributes=self.attributes)
