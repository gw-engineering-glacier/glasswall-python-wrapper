

from glasswall.content_management.config_elements.config_element import ConfigElement
from glasswall.content_management.config_elements.textList import textList
from glasswall.content_management.policies.policy import Policy
from glasswall.content_management.switches.switch import Switch


class textSearchConfig(ConfigElement):
    """ A textSearchConfig ConfigElement.

    textSearchConfig(
        libVersion="core2",
        textList_subelements=[
            {"name": "textItem", "switches": [
                {"name": "text", "value": "generic"},
                {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
            ]}
        ]
    )
    """

    def __init__(self, attributes: dict = {}, textList_subelements: list = [], **kwargs):
        self.name = self.__class__.__name__
        self.attributes = attributes or {}
        self.attributes = {
            **{
                "libVersion": kwargs.get("libVersion", "core2"),
            },
            **self.attributes,
        }
        subelements = []
        for textList_dict in textList_subelements:
            switch_list = []
            for switch_dict in textList_dict.get("switches", []):
                # Construct switch
                switch = Switch(
                    **Policy.get_switches(switch_dict),
                    attributes=Policy.get_attributes(switch_dict)
                )

                # Append switch to switch_list
                switch_list.append(switch)

            # Overwrite textList_dict switches with switch_list objects
            textList_dict["switches"] = switch_list

            # Construct config_element
            config_element = ConfigElement(**textList_dict)

            # Append constructed config_element to subelements
            subelements.append(config_element)

        if subelements:
            self.subelements = [
                textList(subelements=subelements)
            ]
        else:
            self.subelements = []

        super().__init__(name=self.name, attributes=self.attributes, subelements=self.subelements)
