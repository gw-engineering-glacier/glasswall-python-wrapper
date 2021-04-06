

import glasswall
from glasswall.content_management.config_elements.archiveConfig import archiveConfig
from glasswall.content_management.config_elements.config_element import ConfigElement
from glasswall.content_management.policies.policy import Policy
from glasswall.content_management.switches.switch import Switch


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
        self.default_config_elements = [
            glasswall.content_management.config_elements.archiveConfig,
            glasswall.content_management.config_elements.pdfConfig,
            glasswall.content_management.config_elements.pptConfig,
            glasswall.content_management.config_elements.tiffConfig,
            glasswall.content_management.config_elements.wordConfig,
            glasswall.content_management.config_elements.xlsConfig,
        ]
        self.config_elements = []

        # Add default config elements
        for config_element in self.default_config_elements:
            if config_element == archiveConfig:
                self.add_config_element(config_element(default=default_archive_manager))
            else:
                self.add_config_element(config_element(default=default))

        # Add customised config elements provided in `config`
        for config_element_name, switches in config.items():
            # Handle archiveConfig special case
            if config_element_name == "archiveConfig":
                archive_config = glasswall.content_management.config_elements.archiveConfig(
                    default=default_archive_manager,
                    attributes=Policy.get_attributes(switches),
                    **Policy.get_switches(switches)
                )
                self.add_config_element(archive_config)
                continue

            # Create config element
            config_element = getattr(
                glasswall.content_management.config_elements,
                config_element_name,
                ConfigElement
            )(default=default)

            for name, value in switches.items():
                # If switch is an attribute, update attributes instead of adding switch
                if name.startswith("@"):
                    config_element.attributes.update({name.replace("@", "", 1): value})
                    continue

                # Create switch
                switch = getattr(
                    config_element.switches_module,
                    name,
                    Switch
                )(name=name, value=value)

                config_element.add_switch(switch)

            self.add_config_element(config_element)

        super().__init__(config_elements=self.config_elements)
