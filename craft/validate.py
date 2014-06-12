""" Validate Craft's objects and data structures. """

# Standard library imports
from re import findall

class SemanticError(Exception):
    """ Raised if there is a semantic error in an object or data structure. """
    pass

def set(data):
    """ Validates a Craft set's data.

    Parameters
        data
            the set's data.
    Raises
        SemanticError
            if the data does not properly represent a Craft Set.
        SemanticError
            if one of the Set's packages are not properly defined
            in its data.
    Returns
        True
            if the data properly represents a valid Craft Set's
            definition.
    """

    if not isinstance(data, dict):
        raise SemanticError

    for name in data.iterkeys():
        if not isinstance(name, str):
            raise SemanticError
        elif not identifier(name):
            raise SemanticError
        elif not isinstance(data[name], dict):
            raise SemanticError

        for version in data[name].iterkeys():
            if not isinstance(version, (str, float, int)):
                raise SemanticError
            elif not identifier(version):
                raise SemanticError
            elif not isinstance(data[name][version], dict):
                raise SemanticError

            for architecture in data[name][version].iterkeys():
                if not isinstance(architecture, str):
                    raise SemanticError
                elif not identifier(architecture):
                    raise SemanticError
                elif not isinstance(data[name][version][architecture], dict):
                    raise SemanticError

                try:
                    package(data[name][version][architecture])
                except SemanticError:
                    raise

    return True

def package(data):
    """ Validates a Craft package's data.

    Parameters
        data
            data representing a Craft package.
    Raises
        SemanticError
            in case the data does not represent a valid Craft package.
    Returns
        True
            if the data properly represents a Craft package's definition.
    """

    try:
        checksums = data['checksums']
        files_static = data['files']['static']
        depends = data['depends']
        conflicts = data['conflicts']
        replaces = data['replaces']
        provides = data['provides']
        groups = data['groups']
        flags = data['flags']
        maintainers = data['information']['maintainers']
        tags = data['information']['tags']
        misc = data['information']['misc']
    except KeyError:
        raise SemanticError
    except TypeError:
        raise SemanticError

    must_be_str_list = [
            files_static, depends, conflicts,
            replaces, provides, groups,
            flags, tags, maintainers
    ]
    for each in must_be_str_list:
        if each is not None:
            if not isinstance(each, list):
                raise SemanticError
            for subeach in each:
                if not isinstance(subeach, str):
                    raise SemanticError

    must_be_str_dict = [
        checksums, misc
    ]
    for each in must_be_str_dict:
        if each is not None:
            if not isinstance(each, dict):
                raise SemanticError
            for subeach in each.iterkeys():
                if not isinstance(subeach, str):
                    raise SemanticError
                elif not isinstance(each[subeach], str):
                    raise SemanticError

    must_be_valid_identifiers = [
            groups, provides
    ]
    for each in must_be_valid_identifiers:
        if each is not None:
            for subeach in each:
                if not identifier(subeach):
                    raise SemanticError

    return True

def configuration(data):
    """ Validates a Craft configuration's data.

    Parameters
        data
            data representing a Craft configuration.
    Raises
        SemanticError
            if the data does not properly represent a Craft configuration.
    Returns
        True
            if the data properly represents a valid Craft configuration.
    """

    if not isinstance(data, dict):
        raise SemanticError

    try:
        repositories = data['repositories']
        if isinstance(repositories, dict):
            for repository in repositories:
                if not isinstance(repositories[repository], dict):
                    raise SemanticError
                target = repositories[repository]['target']
                handler = repositories[repository]['handler']
                if not isinstance(target, str):
                    raise SemanticError
                elif not isinstance(handler, str):
                    raise SemanticError
                try:
                    env = repositories[repository]['env']
                    if not isinstance(env, dict):
                        raise SemanticError
                    for variable in env:
                        if not isinstance(variable, str):
                            raise SemanticError
                except KeyError:
                    pass
        elif repositories is not None:
            raise SemanticError
    except KeyError:
        raise SemanticError

    try:
        architectures = data['architectures']
        if not isinstance(architectures, dict):
            raise SemanticError
        elif not isinstance(architectures['default'], str):
            raise SemanticError
        elif not identifier(architectures['default']):
            raise SemanticError
        elif not isinstance(architectures['enabled'], list):
            raise SemanticError
        elif not architectures['default'] in architectures['enabled']:
            raise SemanticError
    except KeyError:
        raise SemanticError
    for architecture in architectures['enabled']:
        if not isinstance(architecture, str):
            raise SemanticError
        elif not identifier(architecture):
            raise SemanticError

    try:
        groups = data['groups']
    except KeyError:
        raise SemanticError
    if isinstance(groups, list):
        for group in groups:
            if not isinstance(group, str):
                raise SemanticError
    elif groups is not None:
        raise SemanticError

    try:
        db = data['db']
        root = data['root']
    except KeyError:
        raise SemanticError
    if db is not None and not isinstance(db, str):
        raise SemanticError
    elif root is not None and not isinstance(root, str):
        raise SemanticError

    return True

def identifier(target):
    """ Validates an identifier.

    Parameters
        target
            the identifier to be validated.
    Returns
        True
            if the identifier is valid.
        False
            if the identifier is invalid.
    """

    r = findall('([a-z0-9\-\.]+)', str(target))
    if len(r) >= 1:
        if r[0] == target:
            return True
    return False
