""" Set module. """

class NoMatchFound(Exception):
    """ Indicates no unit was found matching the specified criteria. """
    pass

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
            NoMatchFound
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
            raise NoMatchFound

    def get(self, name):
        """ Retrieves a Unit by name.

        Parameters
            name
                name to be searched for.
        Raises
            NoMatchFound
                if no units could be found matching the specified name.
        Returns
            Unit
        """

        name = str(name).lower()

        for unit in self:
            if unit.name == name:
                return unit

        raise NoMatchFound
