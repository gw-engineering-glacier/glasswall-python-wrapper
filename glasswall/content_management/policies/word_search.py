

from glasswall.content_management import config_elements, errors
from glasswall.content_management.config_elements import ConfigElement
from glasswall.content_management.policies import Policy
from glasswall.content_management.switches import Switch


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
        self.config_elements = [
            config_elements.pdfConfig(default=default, **config.get("pdfConfig", {})),
            config_elements.pptConfig(default=default, **config.get("pptConfig", {})),
            config_elements.sysConfig(**config.get("sysConfig", {})),
            config_elements.textSearchConfig(
                attributes={
                    **{"libVersion": "core2"},
                    **Policy.get_attributes_from_dictionary(config.get("textSearchConfig", {}))
                },
                textList_subelements=config.get("textSearchConfig", {}).get("textList", [])
            ),
            config_elements.tiffConfig(default=default, **config.get("tiffConfig", {})),
            config_elements.wordConfig(default=default, **config.get("wordConfig", {})),
            config_elements.xlsConfig(default=default, **config.get("xlsConfig", {})),
        ]
        super().__init__(config_elements=self.config_elements)

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
            raise errors.ConfigElementNotFound("textSearchConfig")

        # Select the ConfigElement named textList
        textList = next(iter(s for s in textSearchConfig.subelements if s.name == "textList"))

        all_textItem_texts = [
            switch.value.lower()
            for textItem in textList.subelements
            for switch in textItem.switches
            if switch.name == "text"
        ]
        if text not in all_textItem_texts:
            raise errors.SwitchNotFound(f"No switch found with name: 'text' and value: '{text}'")

        # If textList has a subelement textItem that contains a switch named "text" with the same .value as arg "text", delete it to avoid duplicates.
        #   (cannot redact "generic" with "*" and also redact "GeNeRiC" with "@")
        for textItem in textList.subelements.copy():
            for switch in textItem.switches:
                if switch.name == "text" and switch.value.lower() == text.lower():
                    textList.subelements.remove(textItem)
                    break
