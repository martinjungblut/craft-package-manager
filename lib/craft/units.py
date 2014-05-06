from abc import ABCMeta, abstractmethod

class Unit(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def target_install(self, targets, installed):
        pass

    @abstractmethod
    def do_install(self):
        pass

    @abstractmethod
    def target_uninstall(self, targets, installed):
        pass

    @abstractmethod
    def do_uninstall(self):
        pass

    @abstractmethod
    def target_upgrade(self, targets, installed):
        pass

    @abstractmethod
    def do_upgrade(self):
        pass

    @abstractmethod
    def target_downgrade(self, targets, installed):
        pass

    @abstractmethod
    def do_downgrade(self):
        pass

class Package(Unit):
    def __init__(self, name, version):
        self.name = str(name)
        self.version = str(version)
        self._tags = []
        self._misc = {}
        self._dependencies = []
        self._conflicts = []
        self._provides = []

    def depends(self, dependency = False):
        if dependency:
            self._dependencies.append(dependency)
        else:
            return self._dependencies

    def conflicts(self, conflict = False):
        if conflict:
            self._conflicts.append(conflict)
        else:
            return self._conflicts

    def tag(self, tag):
        self._tags.append(tag)

    def provides(self, virtual = False):
        if virtual:
            self._provides.append(virtual)
        else:
            return self._provides

    def misc(self, key = False, value = False):
        if key and value:
            self._misc[key] = value
        else:
            return self._misc

class MetaPackage(Package):
    pass

class VirtualPackage(Unit):
    pass

class Group(Unit):
    pass
