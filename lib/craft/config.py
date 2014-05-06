""" Specifies an interface for handling Craft's configuration. """

class ConfigurationError(Exception):
    """ Indicates there is an error in Craft's configuration. """
    pass

class Configuration(object):
    """ Represents Craft's configuration. """

    def __init__(self, data):
        """ data must be a valid Python representation
        of Craft's configuration file.
        In case it is not, ConfigurationError is raised. """
        try:
            if isinstance(data['repositories'], list):
                for repository in data['repositories']:
                    target = data['repositories'][repository]['target']
                    handler = data['repositories'][repository]['handler']
                    if not isinstance(target, str):
                        raise ConfigurationError
                    if not isinstance(handler, str):
                        raise ConfigurationError
            elif data['repositories'] is not None:
                raise ConfigurationError
        except:
            raise ConfigurationError

        try:
            if not isinstance(data['architectures'], dict):
                raise ConfigurationError
            if not isinstance(data['architectures']['default'], str):
                raise ConfigurationError
            if not isinstance(data['architectures']['enabled'], list):
                raise ConfigurationError
            for architecture in data['architectures']['enabled']:
                if not isinstance(architecture, str):
                    raise ConfigurationError
        except ValueError:
            raise ConfigurationError

        try:
            if isinstance(data['groups'], list):
                for group in data['groups']:
                    if not isinstance(group, str):
                        raise ConfigurationError
            elif data['groups'] is not None:
                raise ConfigurationError
        except ValueError:
            raise ConfigurationError

        try:
            fakedb = data['fakedb']
            fakeroot = data['fakeroot']
            if fakedb is not None and not isinstance(fakedb, str):
                raise ConfigurationError
            if fakeroot is not None and not isinstance(fakeroot, str):
                raise ConfigurationError
        except ValueError:
            raise ConfigurationError

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
