""" Functions for validating Craft data structures. """

class SemanticError(Exception):
    """ Raised if there is a semantic error in an object or data structure. """
    pass

def set(structure):
    """ Validates a Craft set's structure.

    Parameters
        structure
            data structure representing a Craft set.
    Raises
        SemanticError
            if the structure does not properly represent a Craft set.
        SemanticError
            if one of the set's packages are not properly defined
            in its structure.
    Returns
        True
            if the structure properly represents a valid Craft set's
            definition.
    """

    if not isinstance(structure, dict):
        raise SemanticError

    for name in structure.iterkeys():
        if not isinstance(name, str):
            raise SemanticError
        elif not isinstance(structure[name], dict):
            raise SemanticError

        for version in structure[name].iterkeys():
            if not isinstance(version, str) and not isinstance(version, float):
                raise SemanticError
            elif not isinstance(structure[name][version], dict):
                raise SemanticError

            for architecture in structure[name][version].iterkeys():
                if not isinstance(architecture, str):
                    raise SemanticError
                elif not isinstance(structure[name][version][architecture], dict):
                    raise SemanticError

                try:
                    package(structure[name][version][architecture])
                except SemanticError:
                    raise

    return True

def package(structure):
    """ Validates a Craft package's structure.

    Parameters
        structure
            data structure representing a Craft package.
    Raises
        SemanticError
            in case the structure does not represent a valid Craft package.
    Returns
        True
            if the structure properly represents a Craft package's definition.
    """

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
        raise SemanticError

    must_be_str_list = [
            files_static, depends, conflicts,
            replaces, provides, groups,
            flags, tags, maintainers
    ]

    for element in must_be_str_list:
        if element is not None:
            if not isinstance(element, list):
                raise SemanticError
            for subelement in element:
                if not isinstance(subelement, str):
                    raise SemanticError

    must_be_str_dict = [
        hashes, misc
    ]

    for element in must_be_str_dict:
        if element is not None:
            if not isinstance(element, dict):
                raise SemanticError
            for subelement in element.iterkeys():
                if not isinstance(subelement, str):
                    raise SemanticError
                elif not isinstance(element[subelement], str):
                    raise SemanticError

    return True

def configuration(structure):
    """ Validates a Craft configuration's structure.

    Parameters
        structure
            a data structure representing a Craft configuration.
    Raises
        SemanticError
            if the structure does not properly represent a Craft configuration.
    Returns
        True
            if the structure properly represents a valid Craft configuration.
    """

    if not isinstance(structure, dict):
        raise SemanticError

    try:
        repositories = structure['repositories']
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
        architectures = structure['architectures']
        if not isinstance(architectures, dict):
            raise SemanticError
        if not isinstance(architectures['default'], str):
            raise SemanticError
        if not isinstance(architectures['enabled'], list):
            raise SemanticError
        if not architectures['default'] in architectures['enabled']:
            raise SemanticError
    except KeyError:
        raise SemanticError
    for architecture in architectures['enabled']:
        if not isinstance(architecture, str):
            raise SemanticError

    try:
        groups = structure['groups']
    except KeyError:
        raise SemanticError
    if isinstance(groups, list):
        for group in groups:
            if not isinstance(group, str):
                raise SemanticError
    elif groups is not None:
        raise SemanticError

    try:
        db = structure['db']
        root = structure['root']
    except KeyError:
        raise SemanticError
    if db is not None and not isinstance(db, str):
        raise SemanticError
    elif root is not None and not isinstance(root, str):
        raise SemanticError

    return True
