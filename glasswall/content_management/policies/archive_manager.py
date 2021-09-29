

import glasswall
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
                    "@recursionDepth": "100",
                    "jpeg": "discard"
                }
            }
        )
    """

    def __init__(self, default: str = "sanitise", default_archive_manager: str = "process", config: dict = {}):
        self.default = default
        self.default_archive_manager = default_archive_manager
        self.default_config_elements = [
            glasswall.content_management.config_elements.archiveConfig(default=default_archive_manager),
            glasswall.content_management.config_elements.pdfConfig(default=default),
            glasswall.content_management.config_elements.pptConfig(default=default),
            glasswall.content_management.config_elements.sysConfig(),
            glasswall.content_management.config_elements.tiffConfig(default=default),
            glasswall.content_management.config_elements.wordConfig(default=default),
            glasswall.content_management.config_elements.xlsConfig(default=default),
        ]
        self.config = config or {}

        super().__init__(
            default=self.default,
            default_archive_manager=default_archive_manager,
            default_config_elements=self.default_config_elements,
            config=self.config,
        )
