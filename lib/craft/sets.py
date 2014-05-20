""" Set module. """

# Craft imports
from units import Unit

class NoMatchFound(Exception):
    """ Indicates no unit or set was found matching the specified criteria. """
    pass

class Set(object):
    """ Represents a set of units or sets themselves. """

    def __init__(self, name, units = [], sets = [])
        """ units must be a list of Unit. TypeError is raised otherwise.
        sets must be a list of Set. TypeError is raised otherwise. """
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

    def search(self, pattern):
        """ Retrieves a list of units or sets based on a pattern, matching
        a substring of each element's name.
        NoMatchFound is raised in case no units or sets were found matching
        the specified pattern. """

        found = []
        for unit in self.units:
            if unit.name.find(pattern) > -1:
                found.append(unit)
        for set in self.sets:
            if set.name.find(pattern) > -1:
                found.append(set)
        if len(found) > 0:
            return found
        else:
            raise NoMatchFound
