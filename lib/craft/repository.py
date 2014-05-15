""" Provides an interface for handling Craft's repositories. """

# Craft imports
from units import Unit

class NoUnitFound(Exception):
    """ Indicates no unit was found matching the specified criteria. """
    pass

class Repository(object):
    """ Represents a repository. """

    #def __init__(self, units, target, handler, env = {}):
        #""" units must be a list of Unit, TypeError is raised otherwise.
        #env must be a dict, TypeError is raised otherwise. """
        #self.units = {}
        #for unit in units:
            #if isinstance(unit, Unit):
                #self.units[unit.name] = unit
            #else:
                #raise TypeError
        #self.target = target
        #self.handler = handler
        #if not isinstance(env, dict):
            #raise TypeError
        #self.env = env

    def __init__(self, units):
        """ units must be a list of Unit, TypeError is raised otherwise. """
        self.units = []
        for unit in units:
            if isinstance(unit, Unit):
                self.units.append(unit)
            else:
                raise TypeError

    def search(self, pattern):
        """ Retrieve a list of units based on a substring.
        NoUnitFound is raised in case no unit could be found. """
        found = []
        for unit in self.units:
            if unit.name.find(pattern) > -1:
                found.append(unit)
        if len(found) > 0:
            return found
        else:
            raise NoUnitFound
