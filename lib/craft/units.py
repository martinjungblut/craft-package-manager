from abc import ABCMeta, abstractmethod

class Installable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_installation(self, targets, installationed):
        pass

    @abstractmethod
    def perform_installation(self):
        pass

class Uninstallable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_uninstallation(self, targets, installationed):
        pass

    @abstractmethod
    def perform_uninstallation(self):
        pass

class Upgradeable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_upgrade(self, targets, installed):
        pass

    @abstractmethod
    def perform_upgrade(self):
        pass

class Downgradeable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_downgrade(self, targets, installed):
        pass

    @abstractmethod
    def perform_downgrade(self):
        pass

class Package(Installable, Uninstallable, Upgradeable, Downgradeable):
    def __init__(self, name, version):
        self.name = str(name)
        self.version = str(version)
        self._tags = []
        self._misc = {}
        self._dependencies = []
        self._conflicts = []
        self._provides = []

    def depends(self, dependency):
        self._dependencies.append(dependency)

    def does_depend(self, dependency = False):
        if dependency:
            try:
                self._dependencies.index(dependency)
                return True
            except ValueError:
                return False
        else:
            return self._dependencies

    def conflicts(self, conflict):
        self._conflicts.append(conflict)

    def does_conflict(self, conflict = False):
        if conflict:
            try:
                self._conflicts.index(conflict)
                return True
            except ValueError:
                return False
        else:
            return self._conflicts

    def provides(self, virtual_package):
        self._provides.append(virtual_package)

    def does_provide(self, virtual_package = False):
        if virtual_package:
            try:
                self._provides.index(virtual_package)
                return True
            except ValueError:
                return False
        else:
            return self._provides

    def tag(self, tag):
        self._tags.append(tag)

    def has_tag(self, tag):
        try:
            self._tags.index(tag)
            return True
        except ValueError:
            return False

    def misc(self, key = False, value = False):
        if key and value:
            self._misc[key] = value
        else:
            return self._misc

class MetaPackage(Package):
    pass

class VirtualPackage(Installable):
    pass

class Group(Installable):
    pass
