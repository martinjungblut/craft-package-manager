""" Interface for loading Craft-related files. """

# Standard library imports
from glob import glob
from re import findall

# Third-party imports
import yaml as libyaml

# Craft imports
import validate
import error
from configuration import Configuration
from sets import Set
from units import Package, VirtualPackage, Group

class YAMLError(Exception):
    """ Abstracts libyaml.YAMLError in a native Craft exception. """
    pass

def yaml(filepath):
    """ Opens a YAML file, parses it and returns its data.

    Parameters
        filepath
            file to be loaded.
    Raises
        YAMLError
            if the file is not a valid YAML file.
        IOError
            if the file could not be read.
    Returns
        object
            The appropriate Python representation of the file's data.
    """

    try:
        filehandle = open(filepath)
    except IOError:
        raise

    try:
        return libyaml.load(filehandle)
    except libyaml.YAMLError:
        raise YAMLError
    finally:
        filehandle.close()

def _set(paths):
    """ Loads a Set from one or more YAML files.

    Parameters
        paths
            iterable having the file paths to be loaded.
    Raises
        IOError
            if one of the files could not be read.
        YAMLError
            if one of the files is not a valid YAML file.
        validate.SemanticError
            if one of the files is semantically invalid.
    Returns
        Set containing all units found in the specified files.
    """

    units = []
    groups = {}
    virtuals = {}
    registry = []

    for path in paths:
        try:
            definition = yaml(path)
            validate.set(definition)
        except IOError:
            raise
        except YAMLError:
            raise
        except validate.SemanticError:
            raise

        repository = findall('([a-zA-Z0-9]+)', path)[-3]

        for name in definition.iterkeys():
            for version in definition[name].iterkeys():
                for architecture in definition[name][version].iterkeys():
                    try:
                        if registry.index(name+str(version)+architecture) >= 0:
                            error.warning("duplicate package found: {0} {1} ({2}) from repository '{3}'. Ignoring...".format(name, str(version), architecture, repository))
                            break
                    except ValueError:
                        registry.append(name+str(version)+architecture)
                    data = definition[name][version][architecture]
                    package = Package(name, version, architecture)
                    if data['hashes'] is not None:
                        package.hashes = data['hashes']
                    if data['files']['static'] is not None:
                        package.files = data['files']
                    if data['depends'] is not None:
                        for dependency in data['depends']:
                            package.depend(dependency)
                    if data['conflicts'] is not None:
                        for conflict in data['conflicts']:
                            package.conflict(conflict)
                    if data['provides'] is not None:
                        for virtual in data['provides']:
                            package.provide(virtual)
                            try:
                                virtuals[virtual].provided_by(package)
                            except KeyError:
                                virtuals[virtual] = VirtualPackage(virtual)
                                virtuals[virtual].provided_by(package)
                    if data['groups'] is not None:
                        for group in data['groups']:
                            package.add_to_group(group)
                            try:
                                groups[group].add(package)
                            except KeyError:
                                groups[group] = Group(group)
                                groups[group].add(package)
                    if data['flags'] is not None:
                        package.flags = data['flags']
                    if data['information']['maintainers'] is not None:
                        package.maintainers = data['information']['maintainers']
                    if data['information']['tags'] is not None:
                        package.tags = data['information']['tags']
                    if data['information']['misc'] is not None:
                        package.misc = data['information']['misc']
                    package.repository = repository
                    units.append(package)

    for group in groups.iterkeys():
        units.append(groups[group])

    for virtual in virtuals.iterkeys():
        units.append(virtuals[virtual])

    return Set(units)

def available(configuration):
    """ Loads the 'available' set.

    Parameters
        configuration
            Configuration object providing the database root directory.
    Raises
        IOError
            in case a repository's metadata file could not be read.
        YAMLError
            in case a repository's metadata file is not a valid YAML file.
        validate.SemanticError
            in case a repository's metadata file is semantically invalid.
    Returns
        'available' Set object having all available units from all
        repositories.
    """

    try:
        return _set(glob(configuration.db+'/available/*/*.yml'))
    except IOError:
        raise
    except YAMLError:
        raise
    except validate.SemanticError:
        raise

def installed(configuration):
    """ Loads the 'installed' Set.

    Parameters
        configuration
            Configuration object providing the database root directory.
    Raises
        IOError
            in case /installed/metadata.yml could not be found.
        YAMLError
            in case /installed/metadata.yml is not a valid YAML file.
        validate.SemanticError
            in case /installed/metadata.yml is semantically invalid.
    Returns
        'installed' Set object having all installed units.
    """

    try:
        return _set([configuration.db+'/installed/metadata.yml'])
    except IOError:
        raise
    except YAMLError:
        raise
    except validate.SemanticError:
        raise

def configuration(filepath):
    """ Loads a Configuration object from a YAML file.

    Parameters
        filepath
            path of the YAML file to be loaded.
    Raises
        IOError
            in case the file could not be read.
        YAMLError
            in case the file is not a valid YAML file.
        validate.SemanticError
            in case the file is semantically invalid.
    Returns
        Configuration
    """

    try:
        definition = yaml(filepath)
        validate.configuration(definition)
    except IOError:
        raise
    except YAMLError:
        raise
    except validate.SemanticError:
        raise

    repositories = definition['repositories']
    default_architecture = definition['architectures']['default']
    architectures = definition['architectures']['enabled']
    groups = definition['groups']
    db = definition['db']
    root = definition['root']

    return Configuration(repositories, architectures, default_architecture, groups, db, root)
