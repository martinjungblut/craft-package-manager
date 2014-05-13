""" Interface for validating Craft-related data structures. """

class RepositoryError(Exception):
    """ Indicates there is an error in a repository's structure. """
    pass

def repository(structure):
    """ Validates a repository's structure.
    Raises RepositoryError in case there is an error in its definition.
    Raises PackageError in case there is an error in
    a package definition.
    Raises MetaPackageError in case there is an error in a
    metapackage definition.
    Returns True on success. """

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
                    type = structure[element][version][architecture]['type']
                except KeyError:
                    raise RepositoryError
                else:
                    if type == 'package':
                        package(structure[element][version][architecture])
                    elif type == 'metapackage':
                        metapackage(structure[element][version][architecture])

    return True

class BasicPackageError(Exception):
    """ Indicates there is an error in a basic package structure. """
    pass

def basicpackage(structure):
    """ Validates a base package structure.
    Raises BasicPackageError in case it is invalid. """
    try:
        hashes = structure['hashes']
        files = structure['files']
        groups = structure['groups']
        relationships = structure['relationships']
        provides = structure['provides']
        misc = structure['information']['misc']
        tags = structure['information']['tags']
    except KeyError:
        raise BasicPackageError

    if hashes is not None:
        if not isinstance(hashes, dict):
            raise BasicPackageError
        for key in hashes.iterkeys():
            if not isinstance(key, str):
                raise BasicPackageError
            elif not isinstance(hashes[key], str):
                raise BasicPackageError

    if not isinstance(files, dict):
        raise BasicPackageError
    try:
        static = files['static']
    except KeyError:
        raise BasicPackageError
    if static is not None:
        if not isinstance(static, list):
            raise BasicPackageError
        for filepath in static:
            if not isinstance(filepath, str):
                raise BasicPackageError

    if not isinstance(relationships, dict):
        raise BasicPackageError
    try:
        depends = relationships['depends']
        conflicts = relationships['conflicts']
    except KeyError:
        raise BasicPackageError
    if depends is not None:
        if not isinstance(depends, list):
            raise BasicPackageError
        for dependency in depends:
            if not isinstance(dependency, str):
                raise BasicPackageError
    if conflicts is not None:
        if not isinstance(conflicts, list):
            raise BasicPackageError
        for conflict in conflicts:
            if not isinstance(conflict, str):
                raise BasicPackageError

    if groups is not None:
        if not isinstance(groups, list):
            raise BasicPackageError
        for group in groups:
            if not isinstance(group, str):
                raise BasicPackageError

    if provides is not None:
        if not isinstance(provides, list):
            raise BasicPackageError
        for virtual in provides:
            if not isinstance(virtual, str):
                raise BasicPackageError

    if tags is not None:
        if not isinstance(tags, list):
            raise BasicPackageError
        for tag in tags:
            if not isinstance(tag, str):
                raise BasicPackageError

    if misc is not None:
        if not isinstance(misc, dict):
            raise BasicPackageError
        for key in misc.iterkeys():
            if not isinstance(key, str):
                raise BasicPackageError
            elif not isinstance(misc[key], str):
                raise BasicPackageError

class PackageError(Exception):
    """ Indicates there is an error in a package's structure. """
    pass

def package(structure):
    """ Validates a package's structure.
    Raises PackageError in case it is invalid. """

    try:
        basicpackage(structure)
    except BasicPackageError:
        raise PackageError

    if structure['hashes'] is None:
        raise PackageError

class MetaPackageError(Exception):
    """ Indicates there is an error in a metapackage's structure. """
    pass

def metapackage(structure):
    """ Validates a metapackage's structure.
    Raises MetaPackageError in case it is invalid. """
    try:
        basicpackage(structure)
    except BasicPackageError:
        raise MetaPackageError

    if structure['relationships']['depends'] is None:
        raise MetaPackageError

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
