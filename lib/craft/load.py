""" Interface for loading Craft-related files. """

# Third-party imports
import yaml as libyaml

# Craft imports
import validate
from configuration import Configuration
from repository import Repository
from units import Package, MetaPackage, VirtualPackage, Group

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

def repository(file_path):
    """ Opens a repository definition file, parses it,
    validates it and returns a Repository object.
    Raises IOError in case the file could not be read.
    Raises YAMLError in case the file is not a valid YAML file.
    Raises RepositoryError in case the file is semantically invalid. """
    definition = yaml(file_path)
    validate.repository(definition)

    units = []
    groups = {}
    virtuals = {}

    for name in definition.iterkeys():
        for version in definition[name].iterkeys():
            for architecture in definition[name][version].iterkeys():
                data = definition[name][version][architecture]
                package = Package(name, version, architecture)
                if data['depends']:
                    for dependency in data['depends']:
                        package.depends(dependency)
                if data['conflicts']:
                    for conflict in data['conflicts']:
                        package.conflicts(conflict)
                if data['provides']:
                    for virtual in data['provides']:
                        package.provides(virtual)
                        try:
                            virtuals[virtual].provided_by(package)
                        except KeyError:
                            virtuals[virtual] = VirtualPackage(virtual)
                            virtuals[virtual].provided_by(package)
                if data['groups']:
                    for group in data['groups']:
                        package.in_group(group)
                        try:
                            groups[group].add(package)
                        except KeyError:
                            groups[group] = Group(group)
                            groups[group].add(package)
                if data['information']['tags']:
                    for tag in data['information']['tags']:
                        package.tag(tag)
                if data['information']['misc']:
                    for key in data['information']['misc'].iterkeys():
                        package.misc(key, data['information']['misc'][key])
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
