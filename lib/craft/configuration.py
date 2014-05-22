""" Provides an interface for handling Craft's configuration. """

class Configuration(object):
    """ Represents Craft's configuration. """

    def __init__(self, structure):
        """ structure must be a valid Python representation
        of Craft's configuration file, previously loaded
        using load.configuration() """

        self.repositories = structure['repositories']
        self.architectures = structure['architectures']
        self.groups = structure['groups']
        self.db = structure['db']
        self.root = structure['root']

    def has_architecture(self, architecture):
        """ Returns True if the architecture is enabled, False otherwise. """

        try:
            self.architectures.index(architecture)
            return True
        except ValueError:
            return False

    def default_architecture(self):
        """ Returns the default architecture. """

        return self.architectures['default']
