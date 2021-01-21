

from glasswall.content_management.switches.switch import Switch


class bmp(Switch):
    """ An ArchiveManager bmp switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class doc(Switch):
    """ An ArchiveManager doc switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class docx(Switch):
    """ An ArchiveManager docx switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class elf(Switch):
    """ An ArchiveManager elf switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class emf(Switch):
    """ An ArchiveManager emf switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class gif(Switch):
    """ An ArchiveManager gif switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class jpeg(Switch):
    """ An ArchiveManager jpeg switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class mp3(Switch):
    """ An ArchiveManager mp3 switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class mp4(Switch):
    """ An ArchiveManager mp4 switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class mpg(Switch):
    """ An ArchiveManager mpg switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class o(Switch):
    """ An ArchiveManager o switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class pdf(Switch):
    """ An ArchiveManager pdf switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class pe(Switch):
    """ An ArchiveManager pe switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class png(Switch):
    """ An ArchiveManager png switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class ppt(Switch):
    """ An ArchiveManager ppt switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class pptx(Switch):
    """ An ArchiveManager pptx switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class tiff(Switch):
    """ An ArchiveManager tiff switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class txt(Switch):
    """ An ArchiveManager txt switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class wav(Switch):
    """ An ArchiveManager wav switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class wmf(Switch):
    """ An ArchiveManager wmf switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class xls(Switch):
    """ An ArchiveManager xls switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)


class xlsx(Switch):
    """ An ArchiveManager xlsx switch. """

    def __init__(self, value: str):
        self.name = self.__class__.__name__
        self.restrict_values = ["no_action", "discard", "process"]
        self.value = value
        super().__init__(name=self.name, value=self.value, restrict_values=self.restrict_values)
