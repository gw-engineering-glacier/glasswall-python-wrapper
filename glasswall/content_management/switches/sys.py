

from glasswall.content_management.switches.switch import Switch


class interchange_type(Switch):
    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["sisl", "xml"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class interchange_pretty(Switch):
    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["false", "true"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)
