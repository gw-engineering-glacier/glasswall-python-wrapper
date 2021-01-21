

from glasswall.content_management.switches.switch import Switch


class geotiff(Switch):
    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["allow", "disallow", "sanitise"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)
