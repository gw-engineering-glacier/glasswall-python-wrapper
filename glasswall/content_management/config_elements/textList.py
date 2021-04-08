

from glasswall.content_management.config_elements.config_element import ConfigElement


class textList(ConfigElement):
    """ A textList ConfigElement. """

    def __init__(self, subelements: list = []):
        self.name = self.__class__.__name__
        self.subelements = subelements
        super().__init__(name=self.name, subelements=self.subelements)
