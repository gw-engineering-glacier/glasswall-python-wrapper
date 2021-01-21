

from glasswall.content_management import config_elements
from glasswall.content_management.policies.policy import Policy


class ArchiveManager(Policy):
    """ A content management policy for ArchiveManager.

    Args:
        default (str): The default action to be performed. (allow, disallow, sanitise)
        default_archive_manager (str): The default action to be performed for archiveConfig. (no_action, discard, process)
        config (dict): Additional configuration settings passed to the ConfigElement with the same name as the key.

    Example:
        ArchiveManager(
            default="allow",
            default_archive_manager="process",
            config={
                "pdfConfig": {"embeddedImages": "disallow"},
                "wordConfig": {"embeddedImages": "disallow"},
                "archiveConfig": {
                    "recursionDepth": "100",
                    "jpeg": "discard"
                }
            }
        )
    """

    def __init__(self, default: str = "sanitise", default_archive_manager: str = "process", config: dict = {}):
        self.config_elements = [
            config_elements.archiveConfig(default=default_archive_manager, **config.get("archiveConfig", {})),
            config_elements.pdfConfig(default=default, **config.get("pdfConfig", {})),
            config_elements.pptConfig(default=default, **config.get("pptConfig", {})),
            config_elements.tiffConfig(default=default, **config.get("tiffConfig", {})),
            config_elements.wordConfig(default=default, **config.get("wordConfig", {})),
            config_elements.xlsConfig(default=default, **config.get("xlsConfig", {})),
        ]
        super().__init__(config_elements=self.config_elements)
