""" Interface for loading Craft-related files. """

# Standard library imports
from glob import iglob

# Third-party imports
import yaml as libyaml

# Craft imports
import validate
from configuration import Configuration
from repository import Repository
from units import Package, VirtualPackage, Group

class YAMLError(Exception):
    """ Abstracts libyaml.YAMLError in a native Craft exception. """
    pass

def yaml(file_path):
    """ Opens a YAML file, parses it and returns its data.
    Raises YAMLError in case the file is not a valid YAML file.
    Raises IOError in case the file could not be read. """
    file_handle = open(file_path)
    try:
        data = libyaml.load(file_handle)
        return data
    except yaml.YAMLError:
        raise YAMLError
    finally:
        file_handle.close()

def repositories(directory):
    """ Opens all repositories' definition files, parses them,
    validates them and returns a Repository object containing all
    their respective units.
    Raises IOError in case one of their files could not be read.
    Raises YAMLError in case one of their files is not a valid YAML file.
    Raises RepositoryError in case one of their files is
    semantically invalid. """

    units = []
    groups = {}
    virtuals = {}

    for repository in iglob(directory+"/repositories/*/"):
        definition = yaml(repository+'metadata.yml')
        validate.repository(definition)

        for name in definition.iterkeys():
            for version in definition[name].iterkeys():
                for architecture in definition[name][version].iterkeys():
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
                            package.in_group(group)
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

    return Repository(units)

def configuration(file_path):
    """ Opens a configuration file, parses it,
    validates it and returns a Configuration object.
    Raises IOError in case the file could not be read.
    Raises YAMLError in case the file is not a valid YAML file.
    Raises ConfigurationError in case the file is semantically invalid. """
    definition = yaml(file_path)
    validate.configuration(definition)
    return Configuration(definition)
