

import glasswall
from glasswall.content_management.config_elements.config_element import ConfigElement
from glasswall.content_management.policies.policy import Policy
from glasswall.content_management.switches.switch import Switch


class WordSearch(Policy):
    """ A content management policy for Word Search.

    WordSearch(default="allow", config={
        "textSearchConfig": {
            "@libVersion": "core2",
            "textList": [
                {"name": "textItem", "switches": [
                    {"name": "text", "value": "generic"},
                    {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                ]},
            ]
        }
    })
    """

    def __init__(self, default: str = "allow", config: dict = {}):
        self.default = default
        self.default_config_elements = [
            glasswall.content_management.config_elements.pdfConfig(default=default),
            glasswall.content_management.config_elements.pptConfig(default=default),
            glasswall.content_management.config_elements.tiffConfig(default=default),
            glasswall.content_management.config_elements.wordConfig(default=default),
            glasswall.content_management.config_elements.xlsConfig(default=default),
        ]
        self.config = config

        super().__init__(
            default=self.default,
            default_config_elements=self.default_config_elements,
            config=self.config,
        )

    def add_textItem(self, text: str, replacementChar: str, textSetting: str = "redact", **kwargs):
        """ Adds a textItem to the textSearchConfig textList subelements. """
        textSearchConfig = next(iter(c for c in self.config_elements if c.name == "textSearchConfig"), None)
        if not textSearchConfig:
            # Add textSearchConfig to ConfigElements
            textSearchConfig = ConfigElement(
                name="textSearchConfig",
                attributes={"libVersion": kwargs.get("libVersion", "core2")},
                subelements=[ConfigElement(name="textList")]
            )
            self.add_config_element(
                config_element=textSearchConfig,
            )

        # Select the ConfigElement named textList
        textList = next(iter(s for s in textSearchConfig.subelements if s.name == "textList"))

        # If textList has a subelement textItem that contains a switch named "text" with the same .value as arg "text", delete it to avoid duplicates.
        #   (cannot redact "generic" with "*" and also redact "generic" with "@")
        for textItem in textList.subelements.copy():
            for switch in textItem.switches:
                if switch.name == "text" and switch.value.lower() == text.lower():
                    # Remove textItem from tetList.subelements using the builtin list .remove method
                    textList.subelements.remove(textItem)
                    break

        # Add textItem to end of textList.subelements
        textList.subelements.append(
            ConfigElement(
                name="textItem",
                switches=[
                    Switch(name="text", value=text),
                    Switch(name="textSetting", attributes={"replacementChar": replacementChar}, value=textSetting)
                ],
            )
        )

        # Don't sort textList: this preserves top-down order for redaction settings.

    def remove_textItem(self, text: str):
        """ Removes a textItem from the textSearchConfig textList subelements. """
        textSearchConfig = next(iter(c for c in self.config_elements if c.name == "textSearchConfig"), None)
        if not textSearchConfig:
            raise glasswall.content_management.errors.config_elements.ConfigElementNotFound("textSearchConfig")

        # Select the ConfigElement named textList
        textList = next(iter(s for s in textSearchConfig.subelements if s.name == "textList"))

        all_textItem_texts = [
            switch.value.lower()
            for textItem in textList.subelements
            for switch in textItem.switches
            if switch.name == "text"
        ]
        if text not in all_textItem_texts:
            raise glasswall.content_management.errors.switches.SwitchNotFound(f"No switch found with name: 'text' and value: '{text}'")

        # If textList has a subelement textItem that contains a switch named "text" with the same .value as arg "text", delete it to avoid duplicates.
        #   (cannot redact "generic" with "*" and also redact "GeNeRiC" with "@")
        for textItem in textList.subelements.copy():
            for switch in textItem.switches:
                if switch.name == "text" and switch.value.lower() == text.lower():
                    textList.subelements.remove(textItem)
                    break
