""" Craft elements. """

# Standard library imports
from abc import ABCMeta, abstractmethod

# Craft imports
import dsl.relationship

class BrokenDependency(Exception):
    """ Raised if a unit depends on an unavailable unit. """
    pass

class Unit(object):
    """ Base unit. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, name):
        """ All units must have a name. """

        self.name = name

    def __str__(self):
        return unicode(self).encode('utf-8')

class Installable(object):
    """ Interface for installable units. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_installation(self, installed, available, already_targeted):
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

class Package(Unit, Installable):
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
        self.temporary_flags = []

    def __unicode__(self):
        return "{0}:{1} {2}".format(self.name, self.architecture, self.version)

    def __eq__(self, other):
        if isinstance(other, (Group, VirtualPackage)):
            if self.name == other.name:
                return True
        elif str(self) == str(other):
            return True
        return False

    def has_checksum(self, checksum=False):
        """ Checks whether the package has a specific checksum, or any
        checksums at all.

        Parameters
            checksum
                checksum to be checked for. if this is False, this method will
                check whether any checksum is specified in the package.
        Returns
            string
                having the checksum's data in case the parameter checksum
                was specified.
            True
                if any checksum is specified.
            False
                if the specified checksum is not specified, or no checksums
                are specified.
        """

        if self.data['checksums']:
            if not checksum:
                return True
            elif self.data['checksums'].has_key(checksum):
                return self.data['checksums'][checksum]
        return False

    def has_flag(self, flag):
        """ Checks whether the package has a specific flag.

        Parameters
            flag
                the flag's name to be checked for.
        Returns
            True
                if the flag was found.
            False
                if the flag was not found.
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

    def has_temporary_flag(self, flag):
        """ Checks whether the package has a specific temporary flag.

        Parameters
            flag
                the temporary flag's name to be checked for.
        Returns
            True
                if the temporary flag was found.
            False
                if the temporary flag was not found.
        """

        if self.temporary_flags.count(flag) >= 1:
            return True
        return False

    def add_temporary_flag(self, flag):
        """ Adds a specific temporary flag to the package.

        Parameters
            flag
                the temporary flag's name to be added.
        Returns
            True
                if the temporary flag was successfully added to the package.
            False
                if the temporary flag could not be added to the package.
        """

        if not self.has_temporary_flag(flag):
            self.temporary_flags.append(flag)
            return True
        return False

    def save_temporary_flags(self):
        """ Saves the current temporary flags
        as regular flags, and erases them from the
        temporary flag cache afterwards. """

        for flag in self.temporary_flags:
            self.add_flag(flag)
        self.temporary_flags = []

    def has_tag(self, tag):
        """ Checks whether the package has a specific tag.

        Parameters
            tag
                the tag's name to be checked for.
        Returns
            True
                if the tag was found.
            False
                if the tag was not found.
        """

        if self.data['information']['tags']:
            if self.data['information']['tags'].count(tag) >= 1:
                return True
        return False

    def dependencies(self):
        if self.data['depends']:
            return self.data['depends']
        return []

    def target_for_installation(self, installed, available, already_targeted):

        self.add_flag('installed-by-user')
        units_to_install = [self]

        for dependency in self.dependencies():
            parsed = dsl.relationship.parse(dependency)
            if not parsed.count(self.architecture):
                parsed.append(self.architecture)
            dependency = '{0}:{1}'.format(parsed[0], parsed[1])
            if not already_targeted.check_relationship(dependency):
                if not installed.check_relationship(dependency):
                    unit = available.check_relationship(dependency)
                    if unit:
                        if isinstance(unit, Package):
                            unit.add_flag('installed-as-dependency')
                        units_to_install.append(unit)
                    else:
                        raise BrokenDependency

        return units_to_install

class VirtualPackage(Unit):
    """ Represents a virtual package. """

    def __init__(self, name):
        super(VirtualPackage, self).__init__(name)
        self.provided = []

    def __unicode__(self):
        return "{0} (virtual package)".format(self.name)

    def __eq__(self, other):
        if isinstance(other, (Group, VirtualPackage, Package)):
            if self.name == other.name:
                return True
        elif str(self) == str(other):
            return True
        return False

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
        self.packages = []

    def __unicode__(self):
        return "{0} (group)".format(self.name)

    def __eq__(self, other):
        if isinstance(other, (Group, VirtualPackage, Package)):
            if self.name == other.name:
                return True
        elif str(self) == str(other):
            return True
        return False

    def add(self, package):
        """ Adds a package to the group.

        Parameters
            package
                Package object to be added.
        """

        self.packages.append(package)

class Set(set):
    """ Represents a set of units. """

    def __init__(self, units = []):
        """ Constructor.

        Parameters
            units
                list of units to be automatically added to the set.
                May be an empty list.
        """

        for unit in units:
            self.add(unit)

    def __contains__(self, key):
        for unit in self:
            if str(unit) == key:
                return unit
        return False

    def search(self, term):
        """ Retrieves a list of units, using their names and tags.

        Parameters
            term
                string to be searched for.
                automatically converted to lowercase.
        Raises
            ValueError
                if no units could be found matching
                the specified term.
        Returns
            list
                having all units found.
        """

        term = str(term).lower()
        found = []

        for unit in self:
            if unit.name.find(term) > -1:
                found.append(unit)
            elif isinstance(unit, Package):
                if unit.has_tag(term):
                    found.append(unit)

        if len(found) > 0:
            return found
        else:
            raise ValueError

    def check_relationship(self, target):
        """ Checks whether the set has an appropriate unit
        matching the other end of a given relationship.

        Parameters
            target
                string describing the other end of a unit relationship.
        Raises
            ValueError
                if no units were found matching the specified
                relationship.
        Returns
            unit
                a unit that confirms the relationship's validness.
        """

        parsed = dsl.relationship.parse(target)

        if parsed:
            for unit in self:
                if isinstance(unit, Package):
                    try:
                        if parsed[0] == unit.name and parsed[1] == unit.architecture:
                            return unit
                    except IndexError:
                        pass
                elif parsed[0] == unit.name:
                    return unit

        return False

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
