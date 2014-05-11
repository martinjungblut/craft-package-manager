""" Interface for validating Craft-related data structures. """

class RepositoryError(Exception):
    """ Indicates there is an error in a repository's structure. """
    pass

def repository(structure):
    """ Validates a repository's structure.
    Returns True in case the structure is valid.
    Raises RepositoryError in case there is an error in its definition.
    Raises PackageError in case there is an error in
    a package definition.
    Raises MetaPackageError in case there is an error in a
    metapackage definition. """

    if not isinstance(structure, dict):
        raise RepositoryError

    for element in structure:
        if not isinstance(element, str):
            raise RepositoryError
        elif not isinstance(structure[element], dict):
            raise RepositoryError

        for version in element:
            if not isinstance(version, str) and not isinstance(version, float):
                raise RepositoryError
            elif not isinstance(structure[element][version], dict):
                raise RepositoryError

            for architecture in version:
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
                        package(metapackage(structure[element][version][architecture]))
                    elif type == 'metapackage':
                        metapackage(structure[element][version][architecture])

    return True

class PackageError(Exception):
    """ Indicates there is an error in a package's structure. """
    pass

def package(structure):
    """ Validates a package's structure.
    Raises PackageError in case it is invalid. """

    try:
        metapackage(structure)
    except MetaPackageError:
        raise PackageError

    if structure['files'] is None:
        raise PackageError

class MetaPackageError(Exception):
    """ Indicates there is an error in a metapackage's structure. """
    pass

def metapackage(structure):
    """ Validates a metapackage's structure.
    Raises MetaPackageError in case it is invalid. """

    try:
        files = structure['files']
        relationships = structure['relationships']
        provides = structure['provides']
        tags = structure['information']['tags']
        misc = structure['information']['misc']
    except KeyError:
        raise MetaPackageError

    if files is not None:
        if not isinstance(files, dict):
            raise MetaPackageError
        try:
            static = files['static']
            hashes = files['hashes']
        except KeyError:
            raise MetaPackageError
        if not isinstance(static, list):
            raise MetaPackageError
        elif not isinstance(hashes, list):
            raise MetaPackageError
        for filepath in static:
            if not isinstance(filepath, str):
                raise MetaPackageError
        for filehash in hashes:
            if not isinstance(filehash, str):
                raise MetaPackageError

    if relationships is not None:
        if not isinstance(relationships, dict):
            raise MetaPackageError
        try:
            depends = relationships['depends']
            conflicts = relationships['conflicts']
        except KeyError:
            raise MetaPackageError
        if not isinstance(depends, list):
            raise MetaPackageError
        elif not isinstance(conflicts, list):
            raise MetaPackageError
        for dependency in depends:
            if not isinstance(dependency, str):
                raise MetaPackageError
        for conflict in conflicts:
            if not isinstance(conflict, str):
                raise MetaPackageError

    if provides is not None:
        if not isinstance(provides, list):
            raise MetaPackageError
        for virtual in provides:
            if not isinstance(virtual, str):
                raise MetaPackageError

    if tags is not None:
        if not isinstance(tags, list):
            raise MetaPackageError
        for tag in tags:
            if not isinstance(tag, str):
                raise MetaPackageError

    if misc is not None:
        if not isinstance(misc, dict):
            raise MetaPackageError
        for key in misc.iterkeys():
            if not isinstance(key, str):
                raise MetaPackageError
            elif not isinstance(misc[key], str):
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
