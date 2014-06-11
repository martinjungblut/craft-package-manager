""" Craft elements. """

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
    """ Interface for installable units. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_installation(self, targets, installed):
        """ Basic prototype. """

        raise NotImplementedError

class Uninstallable(object):
    """ Interface for uninstallable units. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_uninstallation(self, targets, installed):
        """ Basic prototype. """

        raise NotImplementedError

class Upgradeable(object):
    """ Interface for upgradeable units. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_upgrade(self, targets, installed):
        """ Basic prototype. """

        raise NotImplementedError

class Downgradeable(object):
    """ Interface for downgradeable units. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_downgrade(self, targets, installed):
        """ Basic prototype. """

        raise NotImplementedError

class Package(Unit):
    """ Represents a remotely available package. """

    def __init__(self, name, version, architecture, repository, data):
        """ Constructor.

        Parameters
            name
                the package's name.
            version
                the package's version.
            architecture
                the package's architecture.
            repository
                the package's repository.
            data
                the package's data.
        """

        super(Package, self).__init__(name)
        self.version = str(version)
        self.architecture = str(architecture)
        self.repository = repository
        self.data = data

    def has_checksum(self, checksum=False):
        """ Checks whether the package has a checksum.

        Parameters
            checksum
                checksum to be checked for. if this is False, this method will
                check whether any checksum is available.
        Returns
            True
                if the checksum is available.
            False
                if the checksum is not available.
        """

        if self.data['checksums']:
            if not checksum:
                return True
            elif self.data['checksums'].has_key(checksum):
                return True
        return False

    def checksum(self, checksum):
        """ Retrieves a specific checksum's value.

        Parameters
            checksum
                the checksum's name for the value to be retrieved from.
        Returns
            string
                the checksum value, if the specified was a valid one.
            False
                if the specified was a not valid one.
        """

        if self.has_checksum(checksum):
            return self.data['checksums'][checksum]
        else:
            raise ValueError

    def has_flag(self, flag):
        """ Checks whether the package has a specific flag.

        Parameters
            flag
                the flag's name to be checked for.
        Returns
            True
                if the flag has been found.
            False
                if the flag has been found.
        """

        if self.data['flags']:
            if self.data['flags'].count(flag) >= 1:
                return True
        return False

    def add_flag(self, flag):
        """ Adds a specific flag to the package.

        Parameters
            flag
                the flag's name to be added.
        Returns
            True
                if the flag was successfully added to the package.
            False
                if the flag could not be added to the package.
        """

        if not self.has_flag(flag):
            if self.data['flags'] is None:
                self.data['flags'] = []
            self.data['flags'].append(flag)
            return True
        return False

    def __str__(self):
        return "{0}({1}) {2}".format(self.name, self.architecture, self.version)

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
        """ Constructor.

        Parameters
            name
                the group's name.
        """

        super(Group, self).__init__(name)
        self.packages = list()

    def add(self, package):
        """ Adds a package to the group.

        Parameters
            package
                Package object to be added.
        """

        self.packages.append(package)

class Set(list):
    """ Represents a set of units. """

    def __init__(self, units = []):
        """ Constructor.

        Parameters
            units
                list of units to be automatically added to the set.
                May be an empty list.
        """

        for unit in units:
            self.append(unit)

    def search(self, substring):
        """ Retrieves a list of units based on a substring match of each
        unit's name.

        Parameters
            substring
                string to be searched for.
        Raises
            ValueError
                if no units could be found matching the specified substring.
        Returns
            list
                having all units found.
        """

        substring = str(substring).lower()
        found = []
        for unit in self:
            if unit.name.find(substring) > -1:
                found.append(unit)
        if len(found) > 0:
            return found
        else:
            raise ValueError

    def get(self, name):
        """ Retrieves a Unit by name.

        Parameters
            name
                name to be searched for.
        Raises
            ValueError
                if no units could be found matching the specified name.
        Returns
            Unit
        """

        name = str(name).lower()

        for unit in self:
            if unit.name == name:
                return unit

        raise ValueError

class Configuration(object):
    """ Represents a Craft configuration. """

    def __init__(self, data):
        """ Constructor.

        Parameters
            data
                the configuration's data.
        """

        self.data = data

    def architectures(self):
        """ Retrieve the confiuration's architectures. """

        return self.data['architectures']['enabled']

    def repositories(self):
        """ Retrieve the confiuration's repositories. """

        return self.data['repositories']

    def db(self):
        """ Retrieve the confiuration's database directory path. """

        return self.data['db']

    def root(self):
        """ Retrieve the confiuration's root directory path. """

        return self.data['root']

    def is_architecture_enabled(self, architecture):
        """ Checks whether a specific architecture is enabled.

        Parameters
            architecture
                the architecture to be checked.
        Returns
            True
                in case the architecture is enabled.
            False
                in case the architecture is not enabled.
        """

        if architecture in self.data['architectures']:
            return True
        else:
            return False

    def is_unit_allowed(self, unit):
        """ Checks whether a specific unit is allowed to be installed.

        Parameters
            unit
                Unit to be checked.
        Returns
            True
                in case the unit may be installed.
            False
                in case the unit may not be installed.
        """

        if isinstance(unit, Package):
            if not self.is_architecture_enabled(unit.architecture):
                return False
        return True
