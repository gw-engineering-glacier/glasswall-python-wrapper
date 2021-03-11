

from glasswall.content_management import switches
from glasswall.content_management.config_elements.config_element import ConfigElement


class pdfConfig(ConfigElement):
    """ A pdfConfig ConfigElement.

    Args:
        default (str): The default action: allow, disallow, or sanitise.

    Key word arguments can be specified to change individual switch values:
    pdfConfig(default="allow", embedded_images="sanitise")
    """

    def __init__(self, default: str = "sanitise", **kwargs):
        self.name = self.__class__.__name__
        self.switches = [
            switches.pdf.acroform(value=kwargs.get("acroform", default)),
            switches.pdf.actions_all(value=kwargs.get("actions_all", default)),
            switches.pdf.digital_signatures(value=kwargs.get("digital_signatures", default)),
            switches.pdf.embedded_files(value=kwargs.get("embedded_files", default)),
            switches.pdf.embedded_images(value=kwargs.get("embedded_images", default)),
            switches.pdf.external_hyperlinks(value=kwargs.get("external_hyperlinks", default)),
            switches.pdf.internal_hyperlinks(value=kwargs.get("internal_hyperlinks", default)),
            switches.pdf.javascript(value=kwargs.get("javascript", default)),
            switches.pdf.metadata(value=kwargs.get("metadata", default)),
        ]
        super().__init__(name=self.name, switches=self.switches)
