""" Defines a collection of manageable units. """

# Standard library imports
from abc import ABCMeta, abstractmethod

class Unit(object):
    """ Base unit. Abstract. All units must have a name. """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, name):
        """ All units must have a name. """
        self.name = name

class Installable(object):
    """ Defines an interface for installable units. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_installation(self, targets, installed):
        """ Basic prototype. Not yet implemented. """
        raise NotImplementedError

class Uninstallable(object):
    """ Defines an interface for uninstallable units. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_uninstallation(self, targets, installed):
        """ Basic prototype. Not yet implemented. """
        raise NotImplementedError

class Upgradeable(object):
    """ Defines an interface for upgradeable units. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_upgrade(self, targets, installed):
        """ Basic prototype. Not yet implemented. """
        raise NotImplementedError

class Downgradeable(object):
    """ Defines an interface for downgradeable units. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_downgrade(self, targets, installed):
        """ Basic prototype. Not yet implemented. """
        raise NotImplementedError

class Package(Unit):
    """ Represents package. Not yet fully implemented. """

    def __init__(self, name, version, architecture):
        super(Package, self).__init__(name)
        self.version = str(version)
        self.architecture = str(architecture)
        self._tags = []
        self._misc = {}
        self._dependencies = []
        self._conflicts = []
        self._provides = []

    def depends(self, dependency):
        """ Specifies this package depends on some other unit. """
        self._dependencies.append(dependency)

    def does_depend(self, dependency=False):
        """ If dependency is specified, check whether this package
                depends on some other unit.
                Return True if positive, False otherwise.
            If dependency is not specified, return the appropriate
                list of dependencies. """
        if dependency:
            try:
                self._dependencies.index(dependency)
                return True
            except ValueError:
                return False
        else:
            return self._dependencies

    def conflicts(self, conflict):
        """ Specifies this package conflicts with some other unit. """
        self._conflicts.append(conflict)

    def does_conflict(self, conflict=False):
        """ If conflict is specified, check whether this package
                conflicts with some other unit.
                Return True if positive, False otherwise.
            If conflict is not specified, return the appropriate
                list of conflicts. """
        if conflict:
            try:
                self._conflicts.index(conflict)
                return True
            except ValueError:
                return False
        else:
            return self._conflicts

    def provides(self, virtual_package):
        """ Specifies this package provides a virtual package. """
        self._provides.append(virtual_package)

    def does_provide(self, virtual_package=False):
        """ If virtual_package is specified, check whether this package
                provides that virtual package.
                Return True if positive, False otherwise.
            If virtual_package is not specified, return the appropriate
                list of provided virtual packages. """
        if virtual_package:
            try:
                self._provides.index(virtual_package)
                return True
            except ValueError:
                return False
        else:
            return self._provides

    def tag(self, tag):
        """ Add a tag to this package. """
        self._tags.append(tag)

    def has_tag(self, tag):
        """ Checks wether or not this package has a specific tag.
            Return True if positive, False otherwise. """
        try:
            self._tags.index(tag)
            return True
        except ValueError:
            return False

    def misc(self, key=False, value=False):
        """ Retrieve miscellaneous information about the package.
            If key and value are provided, they are used to search
                for the information.
            If they are not provided, return a dict containing all
                miscellaneous information. """
        if key and value:
            self._misc[key] = value
        else:
            return self._misc

class MetaPackage(Package):
    """ Represents a metapackage. Not yet implemented. """

    def __init__(self, name, version, architecture):
        """ Not yet implemented. Always raises NotImplementedError. """
        super(MetaPackage, self).__init__(name, version, architecture)
        raise NotImplementedError

class VirtualPackage(Installable):
    """ Represents a virtual package. Not yet implemented. """

    def __init__(self):
        """ Not yet implemented. Always raises NotImplementedError. """
        raise NotImplementedError

class Group(Installable):
    """ Represents a group of packages. Not yet implemented. """

    def __init__(self):
        """ Not yet implemented. Always raises NotImplementedError. """
        raise NotImplementedError
