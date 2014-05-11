""" Provides an interface for handling Craft's configuration. """

class Configuration(object):
    """ Represents Craft's configuration. """

    def __init__(self, data):
        """ data must be a valid Python representation
        of Craft's configuration file, previously loaded
        using load.configuration() """
        self.repositories = data['repositories']
        self.architectures = data['architectures']
        self.groups = data['groups']
        self.fakedb = data['fakedb']
        self.fakeroot = data['fakeroot']

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
