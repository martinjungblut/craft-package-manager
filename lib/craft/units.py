""" Defines a collection of manageable units. """

# Standard library imports
from abc import ABCMeta, abstractmethod

class Unit(object):
    """ Base unit. """
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
    """ Represents a remotely available package. Not yet fully implemented. """

    def __init__(self, name, version, architecture):
        super(Package, self).__init__(name)
        self.version = str(version)
        self.architecture = str(architecture)
        self.dependencies = []
        self.conflicts = []
        self.replaces = []
        self.provides = []
        self.groups = []
        self.flags = []
        self.maintainers = []
        self.tags = []
        self.misc = {}
        self.hashes = {}
        self.files = {}

    def depend(self, dependency):
        """ Specifies this package depends on one or more other packages. """
        self.dependencies.append(dependency)

    def does_depend(self, dependency=False):
        """ If dependency is specified, check whether this package
                depends on some other unit.
                Return True if positive, False otherwise.
            If dependency is not specified, return the appropriate
                list of dependencies. """
        if dependency:
            try:
                self.dependencies.index(dependency)
                return True
            except ValueError:
                return False
        else:
            return self.dependencies

    def conflict(self, conflict):
        """ Specifies this package conflicts with one or more
        other packages. """
        self.conflicts.append(conflict)

    def does_conflict(self, conflict=False):
        """ If conflict is specified, check whether this package
                conflicts with some other unit.
                Return True if positive, False otherwise.
            If conflict is not specified, return the appropriate
                list of conflicts. """
        if conflict:
            try:
                self.conflicts.index(conflict)
                return True
            except ValueError:
                return False
        else:
            return self.conflicts

    def replace(self, replacement):
        """ Specifies this package replaces one or more other packages. """
        self.replaces.append(replacement)

    def does_replace(self, replacement=False):
        """ If replacement is specified, check whether this package
                replaces some other unit.
                Return True if positive, False otherwise.
            If replacement is not specified, return the appropriate
                list of replacements. """
        if replacement:
            try:
                self.replaces.index(replacement)
                return True
            except ValueError:
                return False
        else:
            return self.replaces

    def provide(self, virtual):
        """ Specifies this package provides one or more
        virtual packages. """
        self.provides.append(virtual)

    def does_provide(self, virtual=False):
        """ If virtual is specified, check whether this package
                provides that virtual package.
                Return True if positive, False otherwise.
            If virtual is not specified, return the appropriate
                list of provided virtual packages. """
        if virtual:
            try:
                self.provides.index(virtual)
                return True
            except ValueError:
                return False
        else:
            return self.provides

    def has_tag(self, tag):
        """ Checks whether or not this package has a specific tag.
            Return True if positive, False otherwise. """
        try:
            self.tags.index(tag)
            return True
        except ValueError:
            return False

    def has_flag(self, flag):
        """ Checks whether or not this package has a specific flag.
            Return True if positive, False otherwise. """
        try:
            self.flags.index(flag)
            return True
        except ValueError:
            return False

    def is_in_group(self, group):
        """ Checks whether or not this package is in a specific group.
            Return True if positive, False otherwise. """
        try:
            self.groups.index(group)
            return True
        except ValueError:
            return False

class VirtualPackage(Unit):
    """ Represents a virtual package. """

    def __init__(self, name):
        super(VirtualPackage, self).__init__(name)
        self.provided = set()

    def provided_by(self, package):
        self.provided.add(package)

class Group(Unit):
    """ Represents a group of packages. """

    def __init__(self, name):
        super(Group, self).__init__(name)
        self.packages = set()
    
    def add(self, package):
        self.packages.add(package)
