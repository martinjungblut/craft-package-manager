""" High-level interface to Craft's most common operations. """

# Standard library imports
from glob import glob
from os import system, mkdir, chdir, rmdir, remove, rename, access, W_OK
from os.path import isfile, isdir
from shutil import rmtree

# Craft imports
from elements import BrokenDependency, Conflict
from elements import Incompatible, Installable, Uninstallable, Upgradeable, Downgradeable
from elements import Set
import archive
import checksum
import dump
import environment
import message

class InstallError(Exception):
    """ Raised if an error occurs during a package's installation phase. """

    def __init__(self, package):
        """ Constructor.

        Parameters
            package
                the Package unit that failed to be installed.
        """

        self.package = package

class UninstallError(Exception):
    """ Raised if an error occurs during a package's uninstallation phase. """

    def __init__(self, package):
        """ Constructor.

        Parameters
            package
                the Package unit that failed to be uninstalled.
        """

        self.package = package

class RepositoryError(Exception):
    """ Raised if an invalid repository is specified. """

    def __init__(self, name):
        """ Constructor.

        Parameters
            name
                the repository's name.
        """

        self.name = name

class DownloadError(Exception):
    """ Raised if an error occurs during a package's download phase. """

    def __init__(self, package):
        """ Constructor.

        Parameters
            package
                the Package unit that failed to be downloaded.
        """

        self.package = package

class ClearError(Exception):
    """ Raised if an error occurs during the clear operation's execution. """
    pass

class SyncError(Exception):
    """ Raised if an error occurs during the synchronisation's operation execution. """
    pass

class PackageNotAllowed(Exception):
    """ Raised if a given package is not allowed to be installed due to its CPU
    architecture being disabled. """

    def __init__(self, package):
        """ Constructor.

        Parameters
            package
                the Package unit that is not allowed to be installed.
        """

        self.package = package

class EnableError(Exception):
    """ Raised when it is not possible to enable a local cached repository
    from an archive. """

    def __init__(self, filepath):
        """ Constructor.

        Parameters
            filepath
                absolute filesystem path of the repository's archive
        """

        self.filepath = filepath

def _install(configuration, installed, package, filepath):
    """ Performs a low-level package installation.

    Parameters
        configuration
            a valid Craft Configuration object.
        installed
            Set having all currently installed units on the system.
        package
            the Package unit to be installed.
        filepath
            absolute filesystem path of the package's archive
            to be installed.
    Raises
        InstallError
            if any error occurs during the installation.
        OSError
            if, in case an operation has failed, it is not possible
            to cleanly recover from it.
    Returns
        True
            if the installation was successfully completed.
    """

    architecture = package.architecture
    name = package.name
    version = package.version
    db = configuration.db()
    package_directory = db+'installed/'+name+'/'+version+'/'+architecture
    craft_directories = [
        db+'installed/',
        db+'installed/'+name,
        db+'installed/'+name+'/'+version
    ]

    for each in craft_directories:
        try:
            mkdir(each)
        except OSError:
            pass

    if package in installed:
        message.warning("'{0}' is already installed. Aborting...".format(package))
        raise InstallError(package)

    try:
        mkdir(package_directory)
    except OSError:
        message.warning("failed to create internal directory while installing '{0}'. Aborting...".format(package))
        raise InstallError(package)

    try:
        chdir(package_directory)
    except OSError:
        message.warning("could not access the directory belonging to package '{0}'. Aborting...".format(package))
        raise InstallError(package)

    sha1 = package.has_checksum('sha1')
    if sha1:
        if not filepath:
            message.warning("missing archive filepath for package '{0}'. Aborting...".format(package))
            raise InstallError(package)

        if not checksum.sha1(filepath, sha1):
            message.warning("inconsistent archive provided for package '{0}'. Aborting...".format(package))
            try:
                rmtree(package_directory)
            except OSError:
                raise
            raise InstallError(package)

        package_files = archive.getfiles(filepath)
        if not package_files:
            message.warning("empty archive provided for package '{0}'. Aborting...".format(package))
            try:
                rmtree(package_directory)
            except OSError:
                raise
            raise InstallError(package)

        try:
            package_files_dump_handle = open('files', 'w')
        except IOError:
            message.warning("could not write the file list for package '{0}'. Aborting...".format(package))
            try:
                rmtree(package_directory)
            except OSError:
                raise
            raise InstallError(package)
        else:
            for each in package_files:
                package_files_dump_handle.write(each+'\n')
            package_files_dump_handle.close()

        if not archive.extract(filepath, configuration.root()):
            message.warning("could not extract the archive provided for package '{0}'. Aborting...".format(package))
            try:
                rmtree(package_directory)
            except OSError:
                raise
            raise InstallError(package)

    try:
        if not dump.package(package, 'metadata.yml'):
            message.warning("failed to write metadata.yml for package '{0}'. Aborting...".format(package))
            raise InstallError(package)
    except IOError:
        raise

    installed.add(package)
    return True

def _uninstall(configuration, installed, package, keep_static):
    """ Performs a low-level package uninstallation.

    Parameters
        configuration
            a valid Craft Configuration object.
        installed
            Set having all currently installed units on the system.
        package
            the Package unit to be uninstalled.
        keep_static
            specifies whether the package's static files must be preserved
            or not.
    Raises
        UninstallError
            if any error occurs during the uninstallation.
    Returns
        True
            if the uninstallation was successfully completed.
    """

    architecture = package.architecture
    name = package.name
    version = package.version
    db = configuration.db()
    root = configuration.root()

    if package not in installed:
        message.warning("'{0}' is not installed. Aborting...".format(package))
        raise UninstallError(package)

    try:
        chdir(db+'installed/'+name+'/'+version+'/'+architecture)
    except OSError:
        message.warning("could not access the directory belonging to package '{0}'.".format(package))
        raise UninstallError(package)

    package_files = []
    try:
        handle = open('files')
    except IOError:
        pass
    else:
        package_files = handle.read().splitlines()
        handle.close()

    craft_files = [
        db+'installed/'+name+'/'+version+'/'+architecture+'/metadata.yml',
        db+'installed/'+name+'/'+version+'/'+architecture+'/files',
        db+'installed/'+name+'/'+version+'/'+architecture
    ]

    for each in package_files:
        if not access(root+each, W_OK):
            message.warning("cannot remove file '{0}' from package '{1}'.".format(root+each, package))
            raise UninstallError(package)

    for each in craft_files:
        if isfile(each) or isdir(each):
            if not access(each, W_OK):
                message.warning("cannot remove file '{0}'.".format(each))
                raise UninstallError(package)

    if keep_static:
        for each in package.static():
            try:
                rename(root+each, root+each+'.craft-old')
            except OSError:
                message.warning("could not preserve the following static file: '{0}'.".format(root+each))
                pass

    for each in package_files:
        try:
            if isdir(root+each):
                rmdir(root+each)
            elif isfile(root+each):
                remove(root+each)
        except OSError:
            message.warning("could not delete the following file: '{0}'.".format(root+each))
            pass

    for each in craft_files:
        try:
            if isdir(each):
                rmdir(each)
            elif isfile(each):
                remove(each)
        except OSError:
            message.warning("could not delete the following file: '{0}'.".format(each))
            pass

    try_to_remove = [
        db+'installed/'+name+'/'+version,
        db+'installed/'+name
    ]
    for each in try_to_remove:
        try:
            rmdir(each)
        except OSError:
            break

    installed.remove(package)
    return True

def install(configuration, installed, available, attempt_install):
    """ Returns a collection of units allowed to be installed.
    Resolves dependencies, handles conflicts and checks
    for disabled CPU architectures.

    Parameters
        configuration
            a valid Craft Configuration object.
        installed
            Set having all currently installed units on the system.
        available
            Set having all currently available units on the system.
        attempt_install
            iterable having all units the user is attempting
            to get installed.
    Raises
        BrokenDependency
            if a dependency could not be resolved.
        Conflict
            if a conflict was found between two units.
        PackageNotAllowed
            if at least one of the units targeted for installation
            is not able to be installed due to its CPU architecture
            being disabled.
    Returns
        list
            having all Package units to be installed.
    """

    already_targeted = Set()
    attempt_install = Set(attempt_install)
    to_install = Set()

    # Remove all already installed units from the list
    for unit in list(attempt_install):
        if unit in installed:
            message.simple("'{0}' is already installed. Ignoring...".format(unit))
            attempt_install.remove(unit)

    # Target units for installation
    for unit in list(attempt_install):
        if isinstance(unit, Installable):
            try:
                unit.target_for_installation(installed, available, attempt_install, already_targeted, to_install)
            except BrokenDependency:
                raise
        else:
            message.simple("'{0}' is not installable. Ignoring...".format(unit))

    # Check if any of the units is not allowed due to one their CPU
    # architectures not being enabled
    for unit in to_install:
        if not configuration.is_unit_allowed(unit):
            message.simple("'{0}' is not allowed to be installed since its architecture is not currently enabled.".format(unit))
            raise PackageNotAllowed(unit)

    # Check for conflicts
    for unit in to_install:
        if isinstance(unit, Incompatible):
            try:
                unit.check_for_conflicts(installed, to_install)
            except Conflict:
                raise

    return to_install

def uninstall(installed, attempt_uninstall):
    """ Returns a collection of units allowed to be uninstalled.

    Parameters
        installed
            Set having all currently installed units on the system.
        attempt_uninstall
            an iterable having all units the user is attempting
            to get uninstalled.
    Returns
        list
            having all Package units to be uninstalled.
    """

    already_targeted = Set()
    attempt_uninstall = Set(attempt_uninstall)
    to_uninstall = Set()

    # Ignore units which are not installed
    for unit in list(attempt_uninstall):
        if unit not in installed:
            message.simple("'{0}' is not installed and therefore cannot be uninstalled. Ignoring...".format(unit))
            attempt_uninstall.remove(unit)

    # Target units for uninstallation
    for unit in list(attempt_uninstall):
        if isinstance(unit, Uninstallable):
            unit.target_for_uninstallation(installed, attempt_uninstall, already_targeted, to_uninstall)
        else:
            message.simple("'{0}' is not uninstallable. Ignoring...".format(unit))

    return to_uninstall

def upgrade(configuration, installed, available, attempt_upgrade):
    """ Returns a collection of units for performing an upgrade.

    Parameters
        configuration
            a valid Craft Configuration object.
        installed
            Set having all currently installed units on the system.
        available
            Set having all currently available units on the system.
        attempt_upgrade 
            an iterable having all units the user is attempting
            to get to be upgraded.
    Raises
        BrokenDependency
            if a dependency could not be resolved.
        Conflict
            if a conflict was found between two units.
        PackageNotAllowed
            if at least one of the units targeted for installation
            is not able to be installed due to its CPU architecture
            being disabled.
    Returns
        list
            having the units that must be installed, and are replacing older
            units, the units to be uninstalled, and are being replaced,
            and the newly found dependencies.
    """

    already_targeted_for_installation = Set()
    already_targeted_for_upgrade = Set()
    attempt_upgrade = Set(attempt_upgrade)
    to_install = Set()
    to_uninstall = Set()

    # Ignore units which are not installed
    for unit in list(attempt_upgrade):
        if unit not in installed:
            message.simple("'{0}' is not installed and therefore cannot be upgraded. Ignoring...".format(unit))
            attempt_upgrade.remove(unit)

    for unit in attempt_upgrade:
        if isinstance(unit, Upgradeable):
            try:
                unit.target_for_upgrade(installed, available, already_targeted_for_upgrade, already_targeted_for_installation, to_install, to_uninstall)
            except BrokenDependency:
                raise
        else:
            message.simple("'{0}' is not upgradeable. Ignoring...".format(unit))

    # Check if any of the units is not allowed due to one their CPU
    # architectures not being enabled
    for unit in to_install:
        if not configuration.is_unit_allowed(unit):
            message.simple("'{0}' is not allowed to be installed since its architecture is not currently enabled.".format(unit))
            raise PackageNotAllowed(unit)

    # Check for conflicts
    for unit in to_install:
        if isinstance(unit, Incompatible):
            try:
                unit.check_for_conflicts(installed, to_install)
            except Conflict:
                raise

    return [to_install, to_uninstall]

def downgrade(configuration, installed, available, attempt_downgrade):
    """ Returns a collection of units for performing an downgrade.

    Parameters
        configuration
            a valid Craft Configuration object.
        installed
            Set having all currently installed units on the system.
        available
            Set having all currently available units on the system.
        attempt_downgrade
            an iterable having all units the user is attempting
            to get to be downgraded.
    Raises
        BrokenDependency
            if a dependency could not be resolved.
        Conflict
            if a conflict was found between two units.
        PackageNotAllowed
            if at least one of the units targeted for installation
            is not able to be installed due to its CPU architecture
            being disabled.
    Returns
        list
            having the units that must be installed, and are replacing older
            units, the units to be uninstalled, and are being replaced,
            and the newly found dependencies.
    """

    already_targeted_for_installation = Set()
    already_targeted_for_downgrade = Set()
    attempt_downgrade = Set(attempt_downgrade)
    to_install = Set()
    to_uninstall = Set()

    # Ignore units which are not installed
    for unit in list(attempt_downgrade):
        if unit not in installed:
            message.simple("'{0}' is not installed and therefore cannot be downgraded. Ignoring...".format(unit))
            attempt_downgrade.remove(unit)

    for unit in attempt_downgrade:
        if isinstance(unit, Downgradeable):
            try:
                unit.target_for_downgrade(installed, available, already_targeted_for_downgrade, already_targeted_for_installation, to_install, to_uninstall)
            except BrokenDependency:
                raise
        else:
            message.simple("'{0}' is not downgradeable. Ignoring...".format(unit))

    # Check if any of the units is not allowed due to one their CPU
    # architectures not being enabled
    for unit in to_install:
        if not configuration.is_unit_allowed(unit):
            message.simple("'{0}' is not allowed to be installed since its architecture is not currently enabled.".format(unit))
            raise PackageNotAllowed(unit)

    # Check for conflicts
    for unit in to_install:
        if isinstance(unit, Incompatible):
            try:
                unit.check_for_conflicts(installed, to_install)
            except Conflict:
                raise

    return [to_install, to_uninstall]

def download(configuration, packages):
    """ Download packages.

    Parameters
        configuration
            a valid Craft Configuration object.
        packages
            an iterable having the Package units to be downloaded.
    Raises
        RepositoryError
            in case an invalid repository was specified.
        DownloadError
            in case of failure.
    Returns
        True
            in case all specified packages have been successfully downloaded.
    """

    grouped_packages = {}
    db = configuration.db()
    repositories = configuration.repositories()
    packages = list(packages)

    for package in list(packages):
        if isfile(db+'/available/'+package.repository+'/cache/'+package.name+'/'+package.version+'/'+package.architecture+'/package.tar.gz'):
            packages.remove(package)

    for package in packages:
        try:
            grouped_packages[package.repository].append(package)
        except KeyError:
            grouped_packages[package.repository] = []
            grouped_packages[package.repository].append(package)

    for repository_name in grouped_packages.iterkeys():
        try:
            repository = repositories[repository_name]
        except KeyError:
            raise RepositoryError(repository_name) 

        try:
            environment.merge(repository['env'])
        except environment.EnvironmentError:
            message.warning("could not merge the environment variables associated to the repository '{0}'!".format(repository_name))
        except KeyError:
            pass

        for package in grouped_packages[repository_name]:
            if package.has_checksum():
                n = package.name
                v = package.version
                a = package.architecture

                directories = [
                    db+'/available',
                    db+'/available/'+repository_name,
                    db+'/available/'+repository_name+'/cache',
                    db+'/available/'+repository_name+'/cache/'+n,
                    db+'/available/'+repository_name+'/cache/'+n+'/'+v,
                    db+'/available/'+repository_name+'/cache/'+n+'/'+v+'/'+a
                ]

                for directory in directories:
                    try:
                        mkdir(directory)
                    except OSError:
                        pass

                try:
                    chdir(db+'/available/'+package.repository+'/cache/'+n+'/'+v+'/'+a)
                except OSError:
                    raise DownloadError(package)

                if not isfile('package.tar.gz'):
                    handler = repository['handler']
                    target = "{0}/{1}/{2}/{3}/package.tar.gz".format(repository['target'], n, v, a)
                    if system(handler+' '+target) != 0:
                        raise DownloadError(package)

        try:
            environment.purge(repository['env'].keys())
        except environment.EnvironmentError:
            message.warning("could not purge the environment variables associated to the repository '{0}'!".format(package.repository))
        except KeyError:
            pass

    return True

def clear(configuration, cache):
    """ Clears the local cache and repositories' metadata.

    Parameters
        configuration
            a valid Craft Configuration object.
        cache
            specifies whether the package archive cache is
            to be cleared as well. May be True or False.
    Raises
        ClearError
            in case of failure.
    Returns
        True
            in case the local cache has been successfully cleared.
    """

    if cache:
        path = configuration.db()+'/available/*'
    else:
        path = configuration.db()+'/available/*/*.yml'

    for each in glob(path):
        try:
            if isdir(each):
                rmtree(each)
            else:
                remove(each)
        except OSError:
            raise ClearError

    return True

def sync(configuration):
    """ Synchronises enabled repositories from a Craft configuration.

    Parameters
        configuration
            a valid Craft Configuration object.
    Raises
        SyncError
            in case of failure related to the actual synchronisation.
        ClearError
            if the internal clear() call fails and the previously set
            local repository cache is not properly cleared up prior to the
            actual synchronisation.
    Returns
        True
            in case the synchonisation has been successfully executed.
    """

    try:
        clear(configuration, False)
    except ClearError:
        raise

    for name in configuration.repositories().iterkeys():
        repository = configuration.repositories()[name]
        try:
            mkdir(configuration.db()+'available')
        except OSError:
            pass

        try:
            mkdir(configuration.db()+'available/'+name)
        except OSError:
            pass

        try:
            chdir(configuration.db()+'available/'+name)
        except OSError:
            raise SyncError

        try:
            environment.merge(repository['env'])
        except environment.EnvironmentError:
            message.warning("could not merge the environment variables associated to the repository '{0}'!".format(name))
        except KeyError:
            pass

        handler = repository['handler']
        for arch in configuration.architectures():
            target = repository['target']+'/'+arch+'.yml'
            if system(handler+' '+target) != 0:
                message.warning("could not synchronise architecture '{0}' from repository '{1}'!".format(arch, name))

        try:
            environment.purge(repository['env'].keys())
        except environment.EnvironmentError:
            message.warning("could not purge the environment variables associated to the repository '{0}'!".format(name))
        except KeyError:
            pass

    return True

def enable_local_cached_repository(configuration, filepath):
    """ Enables a local cached repository from an archive.

    Parameters
        configuration
            a valid Craft Configuration object.
        filepath
            absolute filesystem path of the repository's archive
    Raises
        EnableError
            if it was not possible to enable the local
            cached repository.
    """

    db = configuration.db()

    try:
        mkdir(db+'available')
    except OSError:
        pass

    if not archive.extract(filepath, db+'available'):
        raise EnableError(filepath)
