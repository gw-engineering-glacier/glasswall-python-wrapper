

import glasswall
from glasswall.content_management.config_elements.config_element import ConfigElement
from glasswall.content_management.policies.policy import Policy
from glasswall.content_management.switches.switch import Switch


class Editor(Policy):
    """ A content management policy for Editor."""

    def __init__(self, default: str = "sanitise", config: dict = {}):
        self.default_config_elements = [
            glasswall.content_management.config_elements.pdfConfig,
            glasswall.content_management.config_elements.pptConfig,
            glasswall.content_management.config_elements.sysConfig,
            glasswall.content_management.config_elements.tiffConfig,
            glasswall.content_management.config_elements.wordConfig,
            glasswall.content_management.config_elements.xlsConfig,
        ]
        self.config_elements = []

        # Add default config elements
        for config_element in self.default_config_elements:
            self.config_elements.append(config_element(default=default))

        # Add customised config elements provided in `config`
        for config_element_name, switches in config.items():
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
