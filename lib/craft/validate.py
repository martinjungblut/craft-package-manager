""" Interface for validating Craft-related data structures. """

class RepositoryError(Exception):
    """ Indicates there is an error in a repository's structure. """
    pass

def repository(structure):
    """ Validates a repository's structure.
    Returns True on success.
    Raises RepositoryError in case there is an error in its definition.
    Raises PackageError in case there is an error in
    a package's definition. """

    if not isinstance(structure, dict):
        raise RepositoryError

    for element in structure.iterkeys():
        if not isinstance(element, str):
            raise RepositoryError
        elif not isinstance(structure[element], dict):
            raise RepositoryError

        for version in structure[element].iterkeys():
            if not isinstance(version, str) and not isinstance(version, float):
                raise RepositoryError
            elif not isinstance(structure[element][version], dict):
                raise RepositoryError

            for architecture in structure[element][version].iterkeys():
                if not isinstance(architecture, str):
                    raise RepositoryError
                elif not isinstance(structure[element][version][architecture], dict):
                    raise RepositoryError

                try:
                    package(structure[element][version][architecture])
                except PackageError:
                    raise

    return True

class PackageError(Exception):
    """ Indicates there is an error in a package's structure. """
    pass

def package(structure):
    """ Validates a package's structure.
    Raises PackageError in case it is invalid. """

    try:
        hashes = structure['hashes']
        files_static = structure['files']['static']
        depends = structure['depends']
        conflicts = structure['conflicts']
        replaces = structure['replaces']
        provides = structure['provides']
        groups = structure['groups']
        flags = structure['flags']
        maintainers = structure['information']['maintainers']
        tags = structure['information']['tags']
        misc = structure['information']['misc']
    except KeyError:
        raise PackageError

    must_be_str_list = [
            files_static, depends, conflicts,
            replaces, provides, groups,
            flags, tags, maintainers
    ]

    for element in must_be_str_list:
        if element is not None:
            if not isinstance(element, list):
                raise PackageError
            for subelement in element:
                if not isinstance(subelement, str):
                    raise PackageError
    
    must_be_str_dict = [
        hashes, misc
    ]

    for element in must_be_str_dict:
        if element is not None:
            if not isinstance(element, dict):
                raise PackageError
            for subelement in element.iterkeys():
                if not isinstance(subelement, str):
                    raise PackageError
                elif not isinstance(element[subelement], str):
                    raise PackageError

class ConfigurationError(Exception):
    """ Indicates there is an error in a configuration structure. """
    pass

def configuration(structure):
    """ Validates a configuration structure.
    Returns True in case the structure is valid.
    Raises ConfigurationError otherwise. """

    if not isinstance(structure, dict):
        raise ConfigurationError

    try:
        repositories = structure['repositories']
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
        architectures = structure['architectures']
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
        groups = structure['groups']
    except KeyError:
        raise ConfigurationError
    if isinstance(groups, list):
        for group in groups:
            if not isinstance(group, str):
                raise ConfigurationError
    elif groups is not None:
        raise ConfigurationError

    try:
        fakedb = structure['fakedb']
        fakeroot = structure['fakeroot']
    except KeyError:
        raise ConfigurationError
    if fakedb is not None and not isinstance(fakedb, str):
        raise ConfigurationError
    elif fakeroot is not None and not isinstance(fakeroot, str):
        raise ConfigurationError

    return True
