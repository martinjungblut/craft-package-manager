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

    def __init__(self, name, version, architecture, repository, data):
        super(Package, self).__init__(name)
        self.version = str(version)
        self.architecture = str(architecture)
        self.data = data
        self.repository = repository

    def hashes(self):
        return self.data['hashes']

    def has_hash(self, hash):
        if self.data['hashes']:
            if self.data['hashes'].has_key(hash):
                return True
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
