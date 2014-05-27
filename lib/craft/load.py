""" Interface for loading Craft-related files. """

# Standard library imports
from glob import glob

# Third-party imports
import yaml as libyaml

# Craft imports
import validate
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

def _repository(filepath, name):
    """ Loads a repository from a YAML file.

    Parameters
        filepath
            file to be loaded.
        name
            used as the repository's name.
    Raises
        IOError
            if the file could not be read.
        YAMLError
            if the file is not a valid YAML file.
        validate.SemanticError
            if the file is semantically invalid.
    """

    units = []
    groups = {}
    virtuals = {}

    try:
        definition = yaml(filepath)
        validate.repository(definition)
    except IOError:
        raise
    except YAMLError:
        raise
    except validate.SemanticError:
        raise

    for packagename in definition.iterkeys():
        for version in definition[packagename].iterkeys():
            for architecture in definition[packagename][version].iterkeys():
                data = definition[packagename][version][architecture]
                package = Package(packagename, version, architecture)
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
                units.append(package)

    for group in groups.iterkeys():
        units.append(groups[group])

    for virtual in virtuals.iterkeys():
        units.append(virtuals[virtual])

    return Set(name, units)

class AvailableError(Exception):
    """ Raised if there is an error in the 'available' set. """
    pass

def available(configuration):
    """ Loads the 'available' set.

    Parameters
        configuration
            Configuration object providing the necessary data.
    Raises
        IOError
            in case a repository's metadata file could not be read.
        YAMLError
            in case a repository's metadata file is not a valid YAML file.
        validate.SemanticError
            in case a repository's metadata file is semantically invalid.
        AvailableError
            in case there are no enabled repositories.
    Returns
        'available' Set object having all enabled repositories as sub-sets.
    """

    repositories = []
    directories = glob(configuration.db+'/available/*/')

    if len(directories) == 0:
        raise AvailableError

    for directory in directories:
        try:
            name = directory.split('/')
            name = name[len(name)-2]
            current = _repository(directory+'metadata.yml', name)
        except validate.SemanticError:
            raise
        repositories.append(current)

    return Set('available', [], repositories)

def installed(configuration):
    """ Loads the 'installed' set.

    Parameters
        configuration
            Configuration object providing the necessary data.
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

    filepath = configuration.db+'/installed/metadata.yml'

    try:
        return _repository(filepath, 'installed')
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

    return Configuration(definition)
