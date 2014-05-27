""" Set module. """

# Craft imports
from units import Unit, Package
from configuration import Configuration

class NoMatchFound(Exception):
    """ Indicates no unit or set was found matching the specified criteria. """
    pass

class Set(object):
    """ Represents a set of units or sets themselves. """

    def __init__(self, name, units = [], sets = []):
        """ Constructor.

        Parameters
            name
                name to be used for the set.
            units
                list of units to be automatically added to the set.
                May be an empty list.
            sets
                list of sets to be automatically added to the set.
                May be an empty list.
        Raises
            TypeError
                if units is not a list of Unit or an empty list.
            TypeError
                if sets is not a list of Set or an empty list.
        """

        if not isinstance(units, list):
            raise TypeError
        if not isinstance(sets, list):
            raise TypeError
        for unit in units:
            if not isinstance(unit, Unit):
                raise TypeError
        for set in sets:
            if not isinstance(set, Set):
                raise TypeError
        self.name = str(name).lower()
        self.units = units
        self.sets = sets

    def search(self, configuration, substring):
        """ Retrieves a list of units based on a substring match of each
        unit's name.

        Parameters
            configuration
                A Configuration object, used for unit filtering.
            substring
                string to be searched for.
        Raises
            NoMatchFound
                if no units could be found matching the specified substring.
            TypeError
                if configuration is not a Configuration object.
        Returns
            list
                having all units found.
        """

        if not isinstance(configuration, Configuration):
            raise TypeError

        substring = str(substring).lower()
        found = []
        for unit in self.units:
            append = False
            if unit.name.find(substring) > -1:
                append = True
                if not configuration.is_unit_allowed(unit):
                    append = False
            if append:
                found.append(unit)
        if len(found) > 0:
            return found
        else:
            raise NoMatchFound

    def get(self, configuration, name):
        """ Retrieves a Unit by name.

        Parameters
            configuration
                A Configuration object, used for unit filtering.
            name
                name to be searched for.
        Raises
            NoMatchFound
                if no units could be found matching the specified name.
        Returns
            Unit
        """
        if not isinstance(configuration, Configuration):
            raise TypeError

        name = str(name).lower()

        for unit in self.units:
            if configuration.is_unit_allowed(unit):
                if unit.name == name:
                    return unit
        raise NoMatchFound
