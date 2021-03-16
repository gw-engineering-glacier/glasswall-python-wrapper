

from glasswall.content_management import config_elements
from glasswall.content_management.policies.policy import Policy


class Editor(Policy):
    """ A content management policy for Editor."""

    def __init__(self, default: str = "sanitise", config: dict = {}):
        self.config_elements = [
            config_elements.pdfConfig(default=default, **{**config.get("pdfConfig", {}), **{"digital_signatures": "disallow"}}),  # force Editor digital_signatures disallow
            config_elements.pptConfig(default=default, **config.get("pptConfig", {})),
            config_elements.sysConfig(**config.get("sysConfig", {})),
            config_elements.tiffConfig(default=default, **config.get("tiffConfig", {})),
            config_elements.wordConfig(default=default, **config.get("wordConfig", {})),
            config_elements.xlsConfig(default=default, **config.get("xlsConfig", {})),
        ]
        super().__init__(config_elements=self.config_elements)
