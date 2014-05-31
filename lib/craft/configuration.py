""" Provides an interface for handling Craft's configuration. """

from units import Package

class Configuration(object):
    """ Represents Craft's configuration. """

    def __init__(self, repositories, architectures, default_architecture, groups, db, root):
        """ Constructor.

        Parameters
            repositories
                dictionary representing all enabled repositories.
            architectures
                list of enabled architectures.
            default_architecture
                architecture to be used as the default.
            groups
                enabled groups.
            db
                base directory to be used as database.
            root
                base directory to be used as manageable filesystem.
        """

        self.repositories = repositories
        self.architectures = architectures
        self.default_architecture = default_architecture
        self.groups = groups
        self.db = db
        self.root = root

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

        if architecture in self.architectures:
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
            if not self.has_architecture(unit.architecture):
                return False
        return True
