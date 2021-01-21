

from typing import Union

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement


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
            **self.attributes,
            **{
                "defaultCompression": kwargs.get("defaultCompression", "zip"),
                "libVersion": kwargs.get("libVersion", "core2"),
                "recursionDepth": kwargs.get("recursionDepth", "2")
            }
        }
        self.switches = [
            switches.archive.bmp(value=kwargs.get("bmp", default)),
            switches.archive.doc(value=kwargs.get("doc", default)),
            switches.archive.docx(value=kwargs.get("docx", default)),
            switches.archive.elf(value=kwargs.get("elf", default)),
            switches.archive.emf(value=kwargs.get("emf", default)),
            switches.archive.gif(value=kwargs.get("gif", default)),
            switches.archive.jpeg(value=kwargs.get("jpeg", default)),
            switches.archive.mp3(value=kwargs.get("mp3", default)),
            switches.archive.mp4(value=kwargs.get("mp4", default)),
            switches.archive.mpg(value=kwargs.get("mpg", default)),
            switches.archive.o(value=kwargs.get("o", default)),
            switches.archive.pdf(value=kwargs.get("pdf", default)),
            switches.archive.pe(value=kwargs.get("pe", default)),
            switches.archive.png(value=kwargs.get("png", default)),
            switches.archive.ppt(value=kwargs.get("ppt", default)),
            switches.archive.pptx(value=kwargs.get("pptx", default)),
            switches.archive.tiff(value=kwargs.get("tiff", default)),
            switches.archive.txt(value=kwargs.get("txt", default)),
            switches.archive.wav(value=kwargs.get("wav", default)),
            switches.archive.wmf(value=kwargs.get("wmf", default)),
            switches.archive.xls(value=kwargs.get("xls", default)),
            switches.archive.xlsx(value=kwargs.get("xlsx", default)),
        ]
        super().__init__(name=self.name, attributes=self.attributes, switches=self.switches)
