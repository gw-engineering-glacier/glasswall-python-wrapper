

from typing import Union

from glasswall.content_management.errors.switches import SwitchNotFound
from glasswall.content_management.switches import Switch


class ConfigElement:
    """ A Content Management Policy configuration element which has a name, and can have attributes, switches, and subelements. """

    def __init__(self, name: str, attributes: Union[dict, type(None)] = None, switches: Union[list, type(None)] = None, subelements: Union[list, type(None)] = None):
        self._indent = 0
        self.name = name
        self.attributes = attributes or {}
        self.switches = switches or []
        self.subelements = subelements or []

        # Sort self.switches by .name and .value
        self.switches.sort()

    def __str__(self):
        return self.text

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
