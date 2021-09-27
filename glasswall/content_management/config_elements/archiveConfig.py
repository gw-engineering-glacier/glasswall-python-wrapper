

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
            self.switches_module.bmp(value=default),
            self.switches_module.doc(value=default),
            self.switches_module.docx(value=default),
            self.switches_module.elf(value=default),
            self.switches_module.emf(value=default),
            self.switches_module.gif(value=default),
            self.switches_module.jpeg(value=default),
            self.switches_module.mp3(value=default),
            self.switches_module.mp4(value=default),
            self.switches_module.mpg(value=default),
            self.switches_module.o(value=default),
            self.switches_module.pdf(value=default),
            self.switches_module.pe(value=default),
            self.switches_module.png(value=default),
            self.switches_module.ppt(value=default),
            self.switches_module.pptx(value=default),
            self.switches_module.tiff(value=default),
            self.switches_module.txt(value=default),
            self.switches_module.wav(value=default),
            self.switches_module.wmf(value=default),
            self.switches_module.xls(value=default),
            self.switches_module.xlsx(value=default),
        ]

        super().__init__(
            name=self.name,
            attributes=self.attributes,
            default=self.default,
            switches_module=self.switches_module,
            default_switches=self.default_switches,
            config=kwargs
        )
