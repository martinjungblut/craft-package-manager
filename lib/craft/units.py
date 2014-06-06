""" Manageable units. """

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
        self.repository = None

    def depend(self, dependency):
        """ Specifies this package depends on one or more other packages. """
        dependency = str(dependency).lower()
        if self.dependencies.count(dependency) == 0:
            self.dependencies.append(dependency)

    def does_depend(self, dependency=False):
        """ If dependency is specified, checks whether this package
                depends on some other unit.
                Returns True if positive, False otherwise.
            If dependency is not specified, returns the appropriate
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
        conflict = str(conflict).lower()
        if self.conflicts.count(conflict) == 0:
            self.conflicts.append(conflict)

    def does_conflict(self, conflict=False):
        """ If conflict is specified, checks whether this package
                conflicts with some other unit.
                Returns True if positive, False otherwise.
            If conflict is not specified, returns the appropriate
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
        replacement = str(replacement).lower()
        if self.replaces.count(replacement) == 0:
            self.replaces.append(replacement)

    def does_replace(self, replacement=False):
        """ If replacement is specified, checks whether this package
                replaces some other unit.
                Returns True if positive, False otherwise.
            If replacement is not specified, returns the appropriate
                list of replacements. """
        if replacement:
            replacement = str(replacement).lower()
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
        virtual = str(virtual).lower()
        if self.provides.count(virtual) == 0:
            self.provides.append(virtual)

    def does_provide(self, virtual=False):
        """ If virtual is specified, checks whether the package
                provides that virtual package.
                Returns True if positive, False otherwise.
            If virtual is not specified, returns the appropriate
                list of provided virtual packages. """
        if virtual:
            virtual = str(virtual).lower()
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
        tag = str(tag).lower()
        try:
            self.tags.index(tag)
            return True
        except ValueError:
            return False

    def has_flag(self, flag):
        """ Checks whether or not this package has a specific flag.
            Return True if positive, False otherwise. """
        flag = str(flag).lower()
        try:
            self.flags.index(flag)
            return True
        except ValueError:
            return False

    def add_to_group(self, group):
        """ Adds the package to a specific group in case it is
        not already in that group. """
        group = str(group).lower()
        if self.groups.count(group) == 0:
            self.groups.append(group)

    def is_in_group(self, group):
        """ Checks whether or not this package is in a specific group.
            Return True if positive, False otherwise. """
        group = str(group).lower()
        try:
            self.groups.index(group)
            return True
        except ValueError:
            return False

    def __str__(self):
        return "{0}:{1} {2}".format(self.name, self.architecture, self.version)

    def __unicode__(self):
        return self.__str__()

    def __eq__(self, other):
        if str(self) == str(other):
            return True
        else:
            return False

class VirtualPackage(Unit):
    """ Represents a virtual package. """

    def __init__(self, name):
        super(VirtualPackage, self).__init__(name)
        self.provided = list()

    def provided_by(self, package):
        self.provided.append(package)

class Group(Unit):
    """ Represents a group of packages. """

    def __init__(self, name):
        super(Group, self).__init__(name)
        self.packages = list()

    def add(self, package):
        self.packages.append(package)
