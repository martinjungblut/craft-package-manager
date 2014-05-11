""" Provides an interface for handling Craft's repositories. """

class UnitNotFound(Exception):
    pass

class Repository(object):
    """ Represents a repository. """

    def __init__(self, data):
        """ data must be a valid Python representation
        of a Craft repository, previously loaded
        using load.repository() """
        self.units = data['units']

    def get(self, unit_name):
        try:
            return self.units[self.units.index(unit_name)]
        except ValueError:
            return UnitNotFound

    # TODO
    def search(self, unit_name):
        return UnitNotFound
