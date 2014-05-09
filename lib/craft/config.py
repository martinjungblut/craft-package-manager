""" Provides an interface for handling Craft's configuration. """

class ConfigurationError(Exception):
    """ Indicates there is an error in Craft's configuration. """
    pass

class Configuration(object):
    """ Represents Craft's configuration. """

    def __init__(self, data):
        """ data must be a valid Python representation
        of Craft's configuration file.
        In case it is not, ConfigurationError is raised. """
        if data is None:
            raise ConfigurationError

        try:
            repositories = data['repositories']
            if isinstance(repositories, dict):
                for repository in repositories:
                    if not isinstance(repositories[repository], dict):
                        raise ConfigurationError
                    target = repositories[repository]['target']
                    handler = repositories[repository]['handler']
                    if not isinstance(target, str):
                        raise ConfigurationError
                    elif not isinstance(handler, str):
                        raise ConfigurationError
                    try:
                        env = repositories[repository]['env']
                        if not isinstance(env, dict):
                            raise ConfigurationError
                        for variable in env:
                            if not isinstance(variable, str):
                                raise ConfigurationError
                    except KeyError:
                        pass
            elif repositories is not None:
                raise ConfigurationError
        except KeyError:
            raise ConfigurationError

        try:
            architectures = data['architectures']
            if not isinstance(architectures, dict):
                raise ConfigurationError
            if not isinstance(architectures['default'], str):
                raise ConfigurationError
            if not isinstance(architectures['enabled'], list):
                raise ConfigurationError
        except KeyError:
            raise ConfigurationError
        for architecture in architectures['enabled']:
            if not isinstance(architecture, str):
                raise ConfigurationError

        try:
            groups = data['groups']
        except KeyError:
            raise ConfigurationError
        if isinstance(groups, list):
            for group in groups:
                if not isinstance(group, str):
                    raise ConfigurationError
        elif groups is not None:
            raise ConfigurationError

        try:
            fakedb = data['fakedb']
            fakeroot = data['fakeroot']
        except KeyError:
            raise ConfigurationError
        if fakedb is not None and not isinstance(fakedb, str):
            raise ConfigurationError
        elif fakeroot is not None and not isinstance(fakeroot, str):
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
