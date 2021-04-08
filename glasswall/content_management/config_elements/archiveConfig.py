

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement


class archiveConfig(ConfigElement):
    """ An archiveConfig ConfigElement.

    Args:
        default (str): The default action: no_action, discard, or process.

    Key word arguments can be specified to change individual switch values:
    archiveConfig(default="no_action", jpeg="discard", pdf="process")
    """

    def __init__(self, default: str = "process", attributes: dict = {}, **kwargs):
        self.name = self.__class__.__name__
        self.default = default
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

        super().__init__(
            name=self.name,
            default=self.default,
            switches_module=self.switches_module,
            default_switches=self.default_switches,
            config=kwargs
        )
