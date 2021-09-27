

from typing import Optional, Union

import glasswall
from glasswall.content_management.errors.switches import SwitchNotFound
from glasswall.content_management.switches import Switch


class ConfigElement:
    """ A Content Management Policy configuration element which has a name, and can have attributes, switches, and subelements. """

    def __init__(self,
                 name: str,
                 attributes: dict = {},
                 switches: list = [],
                 subelements: list = [],
                 default: Optional[str] = None,
                 default_switches: list = [],
                 config: dict = {},
                 switches_module: "glasswall.content_management.switches" = Switch
                 ):
        self._indent = 0
        self.name = name
        self.attributes = attributes or {}
        self.switches = switches or []
        self.subelements = subelements or []
        self.default = default
        self.default_switches = default_switches or []
        self.config = config or {}
        self.switches_module = switches_module

        # Add default switches
        for switch in self.default_switches:
            self.add_switch(switch)

        # Add customised switches provided in `config`
        for switch_name, switch_value in self.config.items():
            # If switch is in switches_module, add it to this config element
            if hasattr(self.switches_module, switch_name):
                self.add_switch(getattr(
                    self.switches_module,
                    switch_name
                )(value=switch_value))

            # Otherwise, create a new Switch and add it
            else:
                self.add_switch(Switch(name=switch_name, value=switch_value))

        # Sort self.switches by .name and .value
        self.switches.sort()

    def __str__(self):
        return self.text

    def __getattr__(self, name):
        # Try to return matching Switch from nonexistant attribute
        switch = next(iter(s for s in self.switches if s.name == name), None)

        if switch:
            return switch

        # or matching subelement from a WordSearch textSearchConfig
        if isinstance(self, glasswall.content_management.config_elements.textSearchConfig):
            subelement = next(iter(s for s in self.subelements if s.name == name), None)
            if subelement:
                return subelement

        raise AttributeError(name)

    def __repr__(self):
        """ Change string representation of object. """
        return f'ConfigElement("{self.name}")'

    def __lt__(self, other):
        """ Used for sorting. Sort by "name" then "switches". """
        return (self.name.lower(), self.switches,) < (other.name.lower(), other.switches,)

    @property
    def text(self):
        """ String representation of XML. """
        indent = " " * 4 * self._indent

        string = f"{indent}<{self.name}"
        # Sort attributes by lowercase key, lowercase value
        for k, v in sorted(self.attributes.items(), key=lambda kv: (str(kv[0]).lower(), str(kv[1]).lower())):
            string += f' {k}="{v}"'
        string += ">"
        for subelement in self.subelements:
            subelement._indent = self._indent + 1
            string += f"\n{subelement.text}"
        for switch in self.switches:
            switch._indent = self._indent + 1
            string += f"\n{switch.text}"
        string += f"\n{indent}</{self.name}>"

        return string

    def get_switch_names(self):
        """ Returns a sorted list of unique Switch.name values from self.switches. """
        return sorted(set(switch.name for switch in self.switches))

    def remove_switch(self, switch: Union[Switch, str]):
        """ Removes all Switch instances from self.switches that match arg "switch".

        Args:
            switch (Union[Switch, str]): A Switch instance or str to match Switch.name.

        Returns:
            self

        Raises:
            glasswall.content_management.errors.switches.SwitchNotFound: The switch was not found.
        """
        if isinstance(switch, Switch):
            # If switch is not in self.switches, raise error.
            if switch not in self.switches:
                raise SwitchNotFound(switch)

            while switch in self.switches:
                # Remove arg "switch" from self.switches using the builtin list .remove method
                self.switches.remove(switch)

        elif isinstance(switch, str):
            # If no Switch in self.switches has a .name matching arg "switch", raise error.
            switch_names = self.get_switch_names()
            if switch not in switch_names:
                raise SwitchNotFound(f"'{switch}' not in {switch_names}")

            # Recreate self.switches, excluding all switches with the same .name as arg "switch"
            self.switches = [f for f in self.switches if f.name != switch]

        else:
            raise TypeError(switch)

    def add_switch(self, switch: Switch, replace: bool = True):
        """ Adds a Switch instance to self.switches.

        Args:
            switch (Switch): A Switch instance.
            replace (bool, optional): Default True. Deletes any pre-existing Switch with the same .name attribute in self.switches.

        Returns:
            self
        """
        if replace:
            # Recreate self.switches, excluding all switches with the same .name as arg "switch"
            self.switches = [f for f in self.switches if f.name != switch.name]

        # Append the new switch
        self.switches.append(switch)

        # Sort self.switches by .name
        self.switches.sort()

        return self
