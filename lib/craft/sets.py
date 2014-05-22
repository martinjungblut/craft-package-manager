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
        """ units must be a list of Unit, or an empty list.
        TypeError is raised otherwise.
        sets must be a list of Set, or an empty list.
        TypeError is raised otherwise. """

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

    def search(self, pattern, configuration):
        """ Retrieves a list of units based on a pattern, matching
        a substring of each unit's name.
        NoMatchFound is raised in case no units were found matching
        the specified pattern. """

        if not isinstance(configuration, Configuration):
            raise TypeError

        pattern = str(pattern).lower()
        found = []
        for unit in self.units:
            append = False
            if unit.name.find(pattern) > -1:
                append = True
                if not configuration.is_unit_allowed(unit):
                    append = False
            if append:
                found.append(unit)
        if len(found) > 0:
            return found
        else:
            raise NoMatchFound
