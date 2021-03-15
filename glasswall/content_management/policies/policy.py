

from typing import Union

from glasswall import utils
from glasswall.content_management.config_elements.config_element import ConfigElement
from glasswall.content_management.errors.config_elements import ConfigElementNotFound
from glasswall.content_management.errors.switches import SwitchNotFound
from glasswall.content_management.switches.switch import Switch


class Policy:
    """ A Content Management Policy made up of a list of ConfigElement instances. """

    def __init__(self, config_elements: Union[list, type(None)] = None):
        self.config_elements = config_elements or []

        # Sort self.config_elements by .name and .switches
        self.config_elements.sort()

    def __str__(self):
        return self.text

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
    def get_attributes_from_dictionary(dictionary: dict):
        """ Returns attributes from arg "dictionary". Attributes are key value pairs that have a key starting with "@". The "@" is excluded in the returned keys. """
        return {
            k[1:]: v
            for k, v in dictionary.items()
            if k.startswith("@")
        }
