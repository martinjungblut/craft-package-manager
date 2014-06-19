""" Craft elements. """

# Standard library imports
from abc import ABCMeta, abstractmethod

# Craft imports
import dsl.relationship

# Exceptions
class BrokenDependency(Exception):
    """ Raised if a unit depends on an unavailable unit. """
    pass

class Conflict(Exception):
    """ Raised if there is a conflict between units. """
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
    def target_for_installation(self, installed, available, targeted):
        raise NotImplementedError

class Uninstallable(object):
    """ Interface for uninstallable units. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_uninstallation(self, targets, installed):
        raise NotImplementedError

class Upgradeable(object):
    """ Interface for upgradeable units. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_upgrade(self, targets, installed):
        raise NotImplementedError

class Downgradeable(object):
    """ Interface for downgradeable units. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def target_for_downgrade(self, targets, installed):
        raise NotImplementedError

class Incompatible(object):
    """ Interface for units that may raise conflicts. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def check_for_conflicts(self, installed, targeted):
        raise NotImplementedError

class Package(Unit, Installable, Incompatible):
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

        if self.data['flags'] is None:
            self.data['flags'] = []

        if flag not in self.data['flags']:
            self.data['flags'].append(flag)
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

        if flag not in self.temporary_flags:
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

    def erase_temporary_flags(self):
        """ Erases the current temporary flags. """

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
            if tag in self.data['information']['tags']:
                return True
        return False

    def dependencies(self):
        if self.data['depends']:
            return self.data['depends']
        return []

    def conflicts(self):
        if self.data['conflicts']:
            return self.data['conflicts']
        return []

    def target_for_installation(self, installed, available, targeted):
        """ Triggered when the package is a target for an
        installation operation.
        This is a recursive method.

        Parameters
            installed
                Set having all currently installed units on the system.
            available
                Set having all currently available units on the system.
            targeted
                Set having all other units that are already
                targeted for installation.
        Raises
            BrokenDependency
                if a dependency could not be satisfied.
        Returns
            list
                having all units that were targeted
                for installation in order for the package to be successfully
                installed. This list includes the package's dependencies.
        """

        units_found = []

        for dependency in self.dependencies():
            if not targeted.target(dependency):
                if not installed.target(dependency):
                    unit = available.target(dependency)
                    if unit:
                        if isinstance(unit, Package):
                            unit.add_temporary_flag('installed-as-dependency')
                        units_found.append(unit)
                    else:
                        raise BrokenDependency

        for unit in units_found:
            targeted.add(unit)

        for unit in units_found:
            targets = unit.target_for_installation(installed, available, targeted)
            if targets:
                for target in targets:
                    targeted.add(target)

        return units_found

    def check_for_conflicts(self, installed, targeted):
        """ Checks whether the package conflicts with any units
        that are already installed or targeted for installation.

        Parameters
            installed
                Set having all currently installed units on the system.
            targeted
                Set having all other units that are already
                targeted for installation.
        Raises
            Conflict
                if a conflict was found.
        """

        for conflict in self.conflicts():
            if installed.target(conflict):
                raise Conflict
            elif targeted.target(conflict):
                raise Conflict

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

    def target_for_installation(self, installed, available, targeted):
        """ Triggered when the virtual package is a target for an
        installation operation.

        Parameters
            installed
                Set having all currently installed units on the system.
            available
                Set having all currently available units on the system.
            targeted
                Set having all other units that are already
                targeted for installation.
        Returns
            list
                having all units that were targeted
                for installation in order for the virtual package to be
                successfully installed.
        """

        organised = {}
        counter = 0
        valid_choice = False

        for package in self.provided:
            organised[counter] = package
            counter = counter+1

        while not valid_choice:
            print("Please choose a package for providing '{0}'.".format(self))
            for each in organised.iterkeys():
                print("{0} - {1}".format(each, organised[each]))

            choice = raw_input()

            try:
                choice = int(choice)
            except ValueError:
                print("The specified value is invalid. Please try again.")
            else:
                if not -1 < choice < len(organised):
                    print("The specified value is invalid. Please try again.")
                else:
                    valid_choice = True

        package = organised[choice]
        print("Your choice was: '{0}'".format(package))

        targeted.add(self)
        targeted.add(package)

        targets = package.target_for_installation(installed, available, targeted)
        if targets:
            for target in targets:
                targeted.add(target)

        return [package]

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

    def target(self, targeting_description):
        """ Targets a specific unit based on a targeting description.

        Parameters
            targeting_description
                string describing a target.
        Returns
            unit
                the targeted unit.
            False
                if no units could be targeted.
        """

        parsed = dsl.relationship.parse(targeting_description)

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

        if architecture in self.architectures():
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
