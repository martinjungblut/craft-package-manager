""" Provides an interface for handling Craft's configuration. """

from units import Unit, Package

class Configuration(object):
    """ Represents Craft's configuration. """

    def __init__(self, structure):
        """ Constructor.

        Parameters
            structure
                must be a valid Python representation of Craft's
                configuration.
        """

        self.repositories = structure['repositories']
        self.architectures = structure['architectures']
        self.groups = structure['groups']
        self.db = structure['db']
        self.root = structure['root']

    def has_architecture(self, architecture):
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

        if architecture in self.architectures['enabled']:
            return True
        else:
            return False

    def default_architecture(self):
        """ Returns the default architecture. """

        return self.architectures['default']

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

        if not isinstance(unit, Unit):
            raise TypeError
        if isinstance(unit, Package):
            if not self.has_architecture(unit.architecture):
                return False
        return True
        
