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
    Raises YAMLError in case the file is not a valid YAML file.
    Raises IOError in case the file could not be read. """

    try:
        file_handle = open(filepath)
    except IOError:
        raise

    try:
        return libyaml.load(file_handle)
    except libyaml.YAMLError:
        raise YAMLError
    finally:
        file_handle.close()

def repository(filepath, name):
    """ Opens a repository definition file, parses it,
    validates it and returns a Set object containing all its units.
    Name is used as the repository's name.
    Raises IOError in case the file could not be read.
    Raises YAMLError in case the file is not a valid YAML file.
    Raises validate.RepositoryError in case the file is
    semantically invalid. """

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
    except validate.RepositoryError:
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

class WorldError(Exception):
    """ Raised if there are no enabled repositories. """
    pass

def world(configuration):
    """ Checks for enabled repositories in a given Configuration object,
    validates them and returns a Set object containing all
    enabled repositories.
    Raises IOError in case one of their files could not be read.
    Raises YAMLError in case one of their files is not a valid YAML file.
    Raises validate.RepositoryError in case one of their files is
    semantically invalid.
    Raises WorldError in case there are no enabled repositories. """

    repositories = []
    directories = glob(configuration.db+'/world/*/')

    if len(directories) == 0:
        raise WorldError

    for directory in directories:
        try:
            name = directory.split('/')
            name = name[len(name)-2]
            current = repository(directory+'metadata.yml', name)
        except validate.RepositoryError:
            raise
        repositories.append(current)

    return Set('world', [], repositories)

def configuration(filepath):
    """ Opens a configuration file, parses it,
    validates it and returns a Configuration object.
    Raises IOError in case the file could not be read.
    Raises YAMLError in case the file is not a valid YAML file.
    Raises validate.ConfigurationError in case the file is
    semantically invalid. """

    try:
        definition = yaml(filepath)
        validate.configuration(definition)
    except IOError:
        raise
    except YAMLError:
        raise
    except validate.ConfigurationError:
        raise

    return Configuration(definition)
