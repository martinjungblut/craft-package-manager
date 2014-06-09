""" Interface for loading Craft-related files. """

# Standard library imports
from glob import glob
from os import access, W_OK, X_OK
from re import findall

# Third-party imports
import yaml as libyaml

# Craft imports
from configuration import Configuration
from sets import Set
from units import Package, VirtualPackage, Group
import error
import validate

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
        structure = libyaml.load(filehandle)
    except libyaml.YAMLError:
        raise YAMLError
    finally:
        filehandle.close()

    return structure

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
    registry = Registry()

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
                version = str(version)
                for architecture in definition[name][version].iterkeys():
                    if registry.has_group_or_virtual(name):
                        error.warning("name conflict between group {0} from repository '{3}' and package {0}({1}) {2}. Ignoring.".format(name, architecture, version, repository))
                    elif registry.has_package(name, version, architecture):
                        error.warning("duplicate package found: {0}({1}) {2} from repository '{3}'. Ignoring.".format(name, architecture, version, repository))
                    else:
                        registry.add_package(name, version, architecture)
                    data = definition[name][version][architecture]
                    package = Package(name, version, architecture)
                    if data['hashes'] is not None:
                        package.hashes = data['hashes']
                    package.files = data['files']
                    if data['depends'] is not None:
                        for dependency in data['depends']:
                            package.depend(dependency)
                    if data['conflicts'] is not None:
                        for conflict in data['conflicts']:
                            package.conflict(conflict)
                    if data['provides'] is not None:
                        for virtual in data['provides']:
                            if registry.has_package(virtual):
                                error.warning("name conflict between virtual package {0} from repository '{3}' and package {0}({1}) {2}. Ignoring.".format(name, architecture, version, repository))
                            elif not registry.has_group_or_virtual(virtual):
                                registry.add_group_or_virtual(virtual)
                            package.provide(virtual)
                            try:
                                virtuals[virtual].provided_by(package)
                            except KeyError:
                                virtuals[virtual] = VirtualPackage(virtual)
                                virtuals[virtual].provided_by(package)
                    if data['groups'] is not None:
                        for group in data['groups']:
                            if registry.has_package(group):
                                error.warning("name conflict between group {0} from repository '{3}' and package {0}({1}) {2}. Ignoring.".format(name, architecture, version, repository))
                            elif not registry.has_group_or_virtual(group):
                                registry.add_group_or_virtual(group)
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
        return _set(glob(configuration.db+'/installed/*/*/*/metadata.yml'))
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

    if not db.endswith('/'):
        db = db+'/'
    if not root.endswith('/'):
        root = root+'/'

    for each in [db, root]:
        if not access(each, W_OK | X_OK):
            raise validate.SemanticError

    return Configuration(repositories, architectures, default_architecture, groups, db, root)

class Registry(dict):
    """ This registry works as an internal namespace. It allows Craft to check
    whether a specific package, virtual package or group has already
    been found. """

    def add_group_or_virtual(self, name):
        """ Adds a group or virtual package to the registry.

        Parameters
            name
                the group's or virtual package's name.
        Returns
            True
                if the group or virtual package was successfully added
                to the registry
            False
                if the group or virtual package was already present
                in the registry, and therefore could not be added.
        """

        if self.has_key(name):
            return False
        else:
            self[name] = True
            return True

    def add_package(self, name, version, architecture):
        """ Adds a package to the registry.

        Parameters
            name
                the package's name.
            version
                the package's version.
            architecture
                the package's architecture.
        Returns
            True
                if the package was successfully added to the registry
            False
                if the package was already present in the registry,
                and therefore could not be added.
        """

        if self.has_key(name):
            if self[name] is True:
                return False
            elif not self[name].has_key(version):
                self[name][version] = {}
                self[name][version][architecture] = True
                return True
            elif not self[name][version].has_key(architecture):
                self[name][version][architecture] = True
                return True
            else:
                return False
        else:
            self[name] = {}
            self[name][version] = {}
            self[name][version][architecture] = True
            return True

    def has_group_or_virtual(self, name):
        """ Checks whether a specific group or virtual package
        is declared in the registry.

        Parameters
            name
                the group's or virtual package's name.
        Returns
            True
                the group or virtual package is declared in the registry.
            False
                the group or virtual package isn't declared in the registry.
        """

        if self.has_key(name) and self[name] is True:
            return True
        else:
            return False


    def has_package(self, name, version=False, architecture=False):
        """ Checks whether a specific package is declared in the registry.

        Parameters
            name
                the package's name.
            version
                the package's version.
                if this parameter is provided, the 'architecture' parameter
                should also be provided. otherwise, they are both ignored.
            architecture
                the package's architecture.
                if this parameter is provided, the 'version' parameter
                should also be provided. otherwise, they are both ignored.
        Returns
            True
                if the package is declared in the registry.
            False
                if the package is not declared in the registry.
        """

        if version and architecture:
            try:
                return self[name][version][architecture]
            except KeyError:
                return False
            except TypeError:
                return False
        elif self.has_key(name) and self[name] is not True:
            return True
        else:
            return False
