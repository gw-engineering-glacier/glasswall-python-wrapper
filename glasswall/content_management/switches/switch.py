

from typing import Optional

from glasswall.content_management.errors.switches import RestrictedValue


class Switch:
    """ A Content Management Policy switch which has a name and a value, and can have attributes. """

    def __init__(self, name: str, value: str, attributes: Optional[dict] = None, restrict_values: Optional[list] = None):
        self._indent = 0
        self.restrict_values = restrict_values or []
        self.name = name
        self.value = value
        self.attributes = attributes or {}

    def __str__(self):
        return self.text

    def __repr__(self):
        """ Change string representation of object. """
        return f'Switch("{self.name}", "{self.value}")'

    def __lt__(self, other):
        """ Used for sorting. Sort by "name" then "value". """
        return (self.name.lower(), self.value.lower(),) < (other.name.lower(), other.value.lower(),)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self.restrict_values and value not in self.restrict_values:
            raise RestrictedValue(f"{self.name} has an unexpected value: '{value}'. Its value is restricted to: {self.restrict_values}")

    @property
    def text(self):
        """ String representation of XML. """
        indent = " " * 4 * self._indent

        string = f"{indent}<{self.name}"
        # Sort attributes by lowercase key, lowercase value
        for k, v in sorted(self.attributes.items(), key=lambda kv: (kv[0].lower(), kv[1].lower())):
            string += f' {k}="{v}"'
        string += f">{self.value}</{self.name}>"

        return string
