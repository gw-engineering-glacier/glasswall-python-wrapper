

from glasswall.content_management.switches.switch import Switch


class dynamic_data_exchange(Switch):
    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["allow", "disallow", "sanitise"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class embedded_files(Switch):
    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["allow", "disallow", "sanitise"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class embedded_images(Switch):
    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["allow", "disallow", "sanitise"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class external_hyperlinks(Switch):
    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["allow", "disallow", "sanitise"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class internal_hyperlinks(Switch):
    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["allow", "disallow", "sanitise"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class macros(Switch):
    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["allow", "disallow", "sanitise"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class metadata(Switch):
    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["allow", "disallow", "sanitise"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class review_comments(Switch):
    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["allow", "disallow", "sanitise"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)
