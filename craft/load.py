""" Load Craft-specific objects. """

# Standard library imports
from glob import glob
from os import access, W_OK, X_OK
from re import findall

# Third-party imports
import yaml as libyaml

# Craft imports
from elements import Package, VirtualPackage, Group, Set, Configuration
from message import warning
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
        data = libyaml.load(filehandle)
    except libyaml.YAMLError:
        raise YAMLError
    finally:
        filehandle.close()

    return data

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
                for architecture in definition[name][version].iterkeys():
                    data = definition[name][version][architecture]
                    package = Package(name, version, architecture, repository, data)

                    try:
                        registry.add_package(name, version, architecture)
                    except PackageInRegistry:
                        warning("duplicate package found: {0}:{1} {2} from repository '{3}'. Ignoring.".format(name, architecture, version, repository))
                        break
                    except GroupInRegistry:
                        warning("name conflict between group {0} from repository '{3}' and package {0}:{1} {2}. Ignoring.".format(name, architecture, version, repository))
                        break
                    except VirtualPackageInRegistry:
                        warning("name conflict between virtual package {0} from repository '{3}' and package {0}:{1} {2}. Ignoring.".format(name, architecture, version, repository))
                        break

                    if data['provides'] is not None:
                        for virtual in data['provides']:
                            try:
                                registry.add_virtual(virtual)
                            except PackageInRegistry:
                                warning("name conflict between virtual package {0} from repository '{3}' and package {0}:{1} {2}. Ignoring.".format(name, architecture, version, repository))
                                break
                            except GroupInRegistry:
                                warning("name conflict between virtual package {0} from repository '{1}' and group {0}. Ignoring.".format(virtual, repository))
                                break

                            try:
                                virtuals[virtual].provided_by(package)
                            except KeyError:
                                virtuals[virtual] = VirtualPackage(virtual)
                                virtuals[virtual].provided_by(package)

                    if data['groups'] is not None:
                        for group in data['groups']:
                            try:
                                registry.add_group(group)
                            except VirtualPackageInRegistry:
                                warning("name conflict between group {0} from repository '{1}' and virtual package {0}. Ignoring.".format(group, repository))
                                break
                            except PackageInRegistry:
                                warning("name conflict between group {0} from repository '{3}' and package {0}:{1} {2}. Ignoring.".format(name, architecture, version, repository))
                                break

                            try:
                                groups[group].add(package)
                            except KeyError:
                                groups[group] = Group(group)
                                groups[group].add(package)

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
        return _set(glob(configuration.db()+'/available/*/*.yml'))
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
        return _set(glob(configuration.db()+'/installed/*/*/*/metadata.yml'))
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
        data = yaml(filepath)
        validate.configuration(data)
    except IOError:
        raise
    except YAMLError:
        raise
    except validate.SemanticError:
        raise

    if not data['db'].endswith('/'):
        data['db'] = data['db']+'/'
    if not data['root'].endswith('/'):
        data['root'] = data['root']+'/'

    for each in [data['db'], data['root']]:
        if not access(each, W_OK | X_OK):
            raise validate.SemanticError

    return Configuration(data)

class GroupInRegistry(Exception):
    """ Indicates the specified group is already present in the registry. """
    pass

class PackageInRegistry(Exception):
    """ Indicates the specified package is already present in the registry. """
    pass

class VirtualPackageInRegistry(Exception):
    """ Indicates the specified virtual package is already present
    in the registry. """
    pass

class Registry(object):
    """ This registry works as an internal namespace. It allows Craft to check
    whether a specific package, virtual package or group has already
    been found. """

    def __init__(self):
        self.virtuals = []
        self.groups = []
        self.packages = []

    def has_group(self, name):
        """ Checks whether a group has already been added to the registry.

        Parameters
            name
                the group's name.
        Returns
            True
                if the group is in the registry.
            False
                if the group is not in the registry.
        """

        if self.groups.count(name) >= 1:
            return True
        else:
            return False

    def has_virtual(self, name):
        """ Checks whether a virtual package has already been added
        to the registry.

        Parameters
            name
                the virtual package's name.
        Returns
            True
                if the virtual package is in the registry.
            False
                if the virtual package is not in the registry.
        """

        if self.virtuals.count(name) >= 1:
            return True
        else:
            return False

    def has_package(self, name, version=False, architecture=False):
        """ Checks whether a package has already been added to the registry.

        Parameters
            name
                the package's name.
            version
                the package's version.
            architecture
                the package's architecture.
        Returns
            True
                if the package is in the registry.
            False
                if the package is not in the registry.
        """

        if version and architecture:
            if self.packages.count('{0} {1} {2}'.format(name, version, architecture)) >= 1:
                return True
        else:
            for package in self.packages:
                if package.split(' ')[0] == name:
                    return True

        return False

    def add_group(self, name):
        """ Adds a group to the registry. May also be used to check
        whether a group has already been added to the registry.

        Parameters
            name
                the group's name.
        Returns
            True
                if the group was successfully added to the registry.
            False
                if the group was already present in the registry,
                and therefore could not be added.
        """

        if self.has_group(name):
            return False
        elif self.has_virtual(name):
            raise VirtualPackageInRegistry
        elif self.has_package(name):
            raise PackageInRegistry
        else:
            self.groups.append(name)
            return True

    def add_virtual(self, name):
        """ Adds a virtual package to the registry. May also be used to check
        whether a virtual package has already been added to the registry.

        Parameters
            name
                the virtual package's name.
        Returns
            True
                if the virtual package was successfully added to the registry.
            False
                if the virtual package was already present in the registry,
                and therefore could not be added.
        """

        if self.has_group(name):
            raise GroupInRegistry
        elif self.has_virtual(name):
            return False
        elif self.has_package(name):
            raise PackageInRegistry
        else:
            self.virtuals.append(name)
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

        if self.has_group(name):
            raise GroupInRegistry
        elif self.has_virtual(name):
            raise VirtualPackageInRegistry
        elif self.has_package(name, version, architecture):
            raise PackageInRegistry
        else:
            self.packages.append('{0} {1} {2}'.format(name, version, architecture))
            return True
