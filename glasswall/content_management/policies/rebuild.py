

from glasswall.content_management import config_elements
from glasswall.content_management.policies.policy import Policy


class Rebuild(Policy):
    """ A content management policy for Rebuild."""

    def __init__(self, default: str = "sanitise", config: dict = {}):
        self.config_elements = [
            config_elements.pdfConfig(default=default, **config.get("pdfConfig", {})),
            config_elements.pptConfig(default=default, **config.get("pptConfig", {})),
            config_elements.sysConfig(**config.get("sysConfig", {})),
            config_elements.tiffConfig(default=default, **config.get("tiffConfig", {})),
            config_elements.wordConfig(default=default, **config.get("wordConfig", {})),
            config_elements.xlsConfig(default=default, **config.get("xlsConfig", {})),
        ]
        super().__init__(config_elements=self.config_elements)
