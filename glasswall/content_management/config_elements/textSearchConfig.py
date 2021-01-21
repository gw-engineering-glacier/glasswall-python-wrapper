

from typing import Union

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

    def __init__(self, attributes: Union[dict, type(None)] = None, textList_subelements: Union[list, type(None)] = None):
        self.name = self.__class__.__name__
        self.attributes = attributes or {}
        subelements = []
        for textList_dict in textList_subelements:
            switch_list = []
            # Construct switches
            for switch_dict in textList_dict.get("switches", []):
                # Get switch attributes
                attributes = Policy.get_attributes_from_dictionary(switch_dict)

                # Remove keys that are switches from switch_dict
                switch_dict = {k: v for k, v in switch_dict.items() if not k.startswith("@")}

                if attributes:
                    # Merge attributes
                    switch_dict = {**switch_dict, **{"attributes": attributes}}

                # Construct switch
                switch = Switch(**switch_dict)

                # Append switch to switch_list
                switch_list.append(switch)

            # Overwrite textList_dict switches with switch_list objects
            textList_dict["switches"] = switch_list

            # Construct config_element
            config_element = ConfigElement(**textList_dict)

            # Append constructed config_element to subelements
            subelements.append(config_element)

        self.subelements = [
            textList(subelements=subelements)
        ]

        super().__init__(name=self.name, attributes=self.attributes, subelements=self.subelements)
