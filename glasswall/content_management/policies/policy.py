

from typing import Optional, Union

import glasswall
from glasswall import utils
from glasswall.content_management.config_elements.config_element import ConfigElement
from glasswall.content_management.errors.config_elements import ConfigElementNotFound
from glasswall.content_management.errors.switches import SwitchNotFound
from glasswall.content_management.switches.switch import Switch
from lxml import etree


class Policy:
    """ A Content Management Policy made up of a list of ConfigElement instances. """

    def __init__(self,
                 config_elements: list = [],
                 default: Optional[str] = None,
                 default_config_elements: list = [],
                 config: dict = {},
                 **kwargs
                 ):
        self.config_elements = config_elements or []
        self.default = default
        self.default_config_elements = default_config_elements or []
        self.config = config or {}

        # Add default config elements
        for config_element in self.default_config_elements:
            self.add_config_element(config_element)

        # Add customised config elements provided in `config`
        for config_element_name, switches in config.items():
            # Create config element
            config_element = getattr(
                glasswall.content_management.config_elements,
                config_element_name,
                ConfigElement
            )

            if config_element == glasswall.content_management.config_elements.archiveConfig:
                # ArchiveManager archiveConfig special case, use default_archive_manager (no_action, discard, process)
                config_element = config_element(default=self.default_archive_manager)
            elif config_element == glasswall.content_management.config_elements.textSearchConfig:
                # WordSearch textSearchConfig special case, pass attributes and subelements
                # construct directly within textSearchConfig as the format is very different
                config_element = config_element(attributes=Policy.get_attributes(switches), textList_subelements=switches.get("textList", []))
                self.add_config_element(config_element)
                continue
            elif config_element == glasswall.content_management.config_elements.ConfigElement:
                # base ConfigElement class
                config_element = config_element(name=config_element_name, default=self.default)
            else:
                # subclasses of ConfigElement that provide their own name
                if hasattr(config_element, "default"):
                    config_element = config_element(default=self.default)
                else:
                    # Don't attempt to set attribute `default` if is not currently set
                    config_element = config_element()

            for switch_name, switch_value in switches.items():
                # If switch is an attribute, update attributes instead of adding switch
                if switch_name.startswith("@"):
                    config_element.attributes.update({switch_name.replace("@", "", 1): switch_value})
                    continue

                # If switch is in switches_module, add it to this config element
                if hasattr(config_element.switches_module, switch_name):
                    config_element.add_switch(getattr(
                        config_element.switches_module,
                        switch_name
                    )(value=switch_value))

                # Otherwise, create a new Switch and add it
                else:
                    config_element.add_switch(Switch(name=switch_name, value=switch_value))

            self.add_config_element(config_element)

        # Sort self.config_elements by .name and .switches
        self.config_elements.sort()

    def __str__(self):
        return self.text

    def __getattr__(self, name):
        # Try to return matching ConfigElement from nonexistant attribute
        config_element = next(iter(c for c in self.config_elements if c.name == name), None)

        if config_element:
            return config_element

        raise AttributeError(name)

    @property
    def text(self):
        """ String representation of XML. """
        string = '<?xml version="1.0" encoding="utf-8"?>'
        string += "\n<config>"
        for config_element in self.config_elements:
            config_element._indent = 1
            string += f"\n{config_element.text}"
        string += '\n</config>'

        return string

    def encode(self, *args):
        """ UTF-8 encoded string representation of XML. """
        return str(self).encode(*args)

    def get_config_element_names(self):
        """ Returns a sorted list of unique ConfigElement.name values from self.config_elements. """
        return sorted(set(config_element.name for config_element in self.config_elements))

    def remove_switch(self, config_element: Union[ConfigElement, str], switch: Union[Switch, str]):
        """ Removes all Switch instances from config_element.switches that match arg "switch" where the ConfigElement instance in self.config_elements matches arg "config_element".

        Args:
            config_element (Union[ConfigElement, str]): A ConfigElement instance or ConfigElement.name to match.
            switch (Union[Switch, str]): A Switch instance or Switch.name to match.

        Returns:
            self

        Raises:
            glasswall.content_management.errors.config_elements.ConfigElementNotFound: The config_element was not found.
            glasswall.content_management.errors.switches.SwitchNotFound: The switch was not found.
        """
        if isinstance(config_element, ConfigElement):
            # If config_element is not in self.config_elements, raise error.
            if config_element not in self.config_elements:
                raise ConfigElementNotFound(config_element)

            # The ConfigElement instance exists in self.config_elements, remove the switch.
            config_element.remove_switch(switch=switch)

        elif isinstance(config_element, str):
            # If no ConfigElement in self.config_elements has a .name matching arg "config_element", raise error.
            config_element_names = self.get_config_element_names()
            if config_element not in config_element_names:
                raise ConfigElementNotFound(f"'{config_element}' not in {config_element_names}")

            matched_config_elements = [c for c in self.config_elements if c.name == config_element]

            if isinstance(switch, Switch):
                matched_config_elements_with_switch = [c for c in matched_config_elements if switch in c.switches]
            elif isinstance(switch, str):
                matched_config_elements_with_switch = [c for c in matched_config_elements if switch in c.get_switch_names()]
            else:
                raise TypeError(switch)

            # If no matching ConfigElement contains arg "switch" in .switches, raise error.
            if not matched_config_elements_with_switch:
                available_switches = sorted(set(utils.flatten_list([c.switches for c in matched_config_elements])))
                switch_name = switch.name if isinstance(switch, Switch) else switch
                raise SwitchNotFound(f"'{switch_name}' not in {available_switches}")

            # Remove arg "switch" from .switches of all ConfigElement instances that contain arg "switch" in .switches.
            for c in matched_config_elements_with_switch:
                c.remove_switch(switch=switch)

        return self

    def add_switch(self, config_element: Union[ConfigElement, str], switch: Switch, replace: bool = True):
        """ Adds a Switch to any ConfigElement in self.config_elements that matches arg "config_element".

        Args:
            config_element (Union[ConfigElement, str]): A ConfigElement instance or str to match ConfigElement.name.
            switch (Switch): A Switch instance.
            replace (bool, optional): Default True. Deletes any pre-existing Switch with the same .name attribute as arg "switch" within a ConfigElement that matches arg "config_element".

        Returns:
            self

        Raises:
            glasswall.content_management.errors.config_elements.ConfigElementNotFound: The config_element was not found.
        """
        if isinstance(config_element, ConfigElement):
            # If config_element is not in self.config_elements, raise error.
            if config_element not in self.config_elements:
                raise ConfigElementNotFound(config_element)

            # The ConfigElement instance exists in self.config_elements, add the switch.
            config_element.add_switch(switch=switch, replace=replace)

        elif isinstance(config_element, str):
            # If no ConfigElement in self.config_elements has a .name matching arg "config_element", raise error.
            config_element_names = self.get_config_element_names()
            if config_element not in config_element_names:
                raise ConfigElementNotFound(f"'{config_element}' not in {config_element_names}")

            # At least one ConfigElement instance with the same .name as arg "config_element" exists, add the switch.
            for c in self.config_elements:
                if c.name == config_element:
                    c.add_switch(switch=switch, replace=replace)

        else:
            raise TypeError(config_element)

        return self

    def remove_config_element(self, config_element: Union[ConfigElement, str]):
        """ Removes all ConfigElement instances from self.config_elements that match arg "config_element".

        Args:
            config_element (Union[ConfigElement, str]): A ConfigElement instance or ConfigElement.name attribute to match.

        Returns:
            self

        Raises:
            glasswall.content_management.errors.config_elements.ConfigElementNotFound: The config_element was not found.
        """
        if isinstance(config_element, ConfigElement):
            # If config_element is not in self.config_elements, raise error.
            if config_element not in self.config_elements:
                raise ConfigElementNotFound(config_element)

            while config_element in self.config_elements:
                # Remove all ConfigElement instances from self.config_elements using the builtin list .remove method
                self.config_elements.remove(config_element)

        elif isinstance(config_element, str):
            # If no ConfigElement in self.config_elements has a .name matching arg "config_element", raise error.
            config_element_names = self.get_config_element_names()
            if config_element not in config_element_names:
                raise ConfigElementNotFound(f"'{config_element}' not in {config_element_names}")

            # Remove all ConfigElement instances with the same .name as arg "config_element"
            self.config_elements = [c for c in self.config_elements if c.name != config_element]

        else:
            raise TypeError(config_element)

        return self

    def add_config_element(self, config_element: ConfigElement, replace=True):
        """ Adds a ConfigElement instance to self.config_elements.

        Args:
            config_element (ConfigElement): A ConfigElement instance.
            replace (bool, optional): Default True. Deletes any pre-existing ConfigElement with the same .name attribute in self.config_elements.

        Returns:
            self
        """
        if not isinstance(config_element, ConfigElement):
            raise TypeError(config_element)

        if replace:
            try:
                # Remove all ConfigElement instances with the same .name as arg "config_element"
                self.remove_config_element(config_element=config_element.name)
            except ConfigElementNotFound:
                # No ConfigElement exists with the same .name as arg "config_element"
                pass

        # Sort the .switches attribute of config_element
        config_element.switches.sort()

        # Append config_element to self.config_elements
        self.config_elements.append(config_element)

        # Sort self.config_elements by .name and .switches
        self.config_elements.sort()

        return self

    @staticmethod
    def get_attributes(dictionary: dict):
        """ Returns attributes from arg "dictionary". Attributes are key value pairs that have a key starting with "@". The "@" is excluded in the returned keys. """
        return {
            k.replace("@", "", 1): v
            for k, v in dictionary.items()
            if k.startswith("@")
        }

    @staticmethod
    def get_switches(dictionary: dict):
        """ Returns switches from arg "dictionary". Switches are key value pairs that do not have a key starting with "@". """
        return {
            k: v
            for k, v in dictionary.items()
            if not k.startswith("@")
        }

    @staticmethod
    def from_string(string: str):
        """ Create Policy object from string.

        Args:
            string (str): A string representation of an xml content management policy, or a file path.

        Returns:
            new_policy (glasswall.content_management.policies.Policy): A Policy object.
        """
        try:
            string = glasswall.utils.validate_xml(string)
        except ValueError:
            raise glasswall.content_management.errors.policies.ContentManagementPolicyError(string)

        config = etree.fromstring(string.encode("utf-8"))

        if config.tag != "config":
            raise glasswall.content_management.errors.policies.ContentManagementPolicyError(string)

        new_policy = glasswall.content_management.policies.Policy()

        for config_element in config:
            if hasattr(glasswall.content_management.config_elements, config_element.tag):
                # Known config element exists, e.g. pdfConfig
                new_config_element = getattr(glasswall.content_management.config_elements, config_element.tag)(attributes=config_element.attrib)
            else:
                # Create custom config element
                new_config_element = glasswall.content_management.config_elements.ConfigElement(name=config_element.tag, attributes=config_element.attrib)

            for item in config_element:
                # Add children, e.g. textList has child elements: textItem
                if item.getchildren():
                    # if getchildren() then item is a config element, such as textList
                    textList = glasswall.content_management.config_elements.ConfigElement(name=item.tag, attributes=item.attrib)
                    for textItem in item.getchildren():
                        new_textItem = glasswall.content_management.config_elements.ConfigElement(name=textItem.tag, attributes=textItem.attrib)
                        for switch in textItem:
                            new_textItem.add_switch(glasswall.content_management.switches.Switch(name=switch.tag, value=switch.text, attributes=switch.attrib))
                        textList.subelements.append(new_textItem)
                    new_config_element.subelements.append(textList)
                    continue

                # if not getchildren() then item is a switch
                if hasattr(new_config_element.switches_module, item.tag):
                    # Known switch exists, e.g. pdf.internal_hyperlinks
                    new_switch = getattr(new_config_element.switches_module, item.tag)(value=item.text)
                else:
                    new_switch = glasswall.content_management.switches.Switch(name=item.tag, value=item.text, attributes=item.attrib)
                new_config_element.add_switch(new_switch)

            new_policy.add_config_element(new_config_element)

        return new_policy
