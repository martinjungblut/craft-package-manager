""" Actions. """

# Standard library imports
from glob import glob
from os import system, mkdir, chdir, rmdir, remove, access, W_OK
from os.path import isfile, isdir
from shutil import rmtree

# Craft imports
from elements import Set, Incompatible, BrokenDependency, Conflict, Package, Group, VirtualPackage
import archive
import checksum
import dump
import environment
import load
import message
import validate

# Exceptions
class InstallError(Exception):
    pass

class UninstallError(Exception):
    pass

class DownloadError(Exception):
    pass

class ClearError(Exception):
    pass

class SyncError(Exception):
    pass

class UnitNotAllowed(Exception):
    """ Raised if a given unit is not allowed to be installed. """
    pass

class Craft(object):
    def __init__(self, filepath):
        """ Constructor.

        Parameters
            filepath
                absolute filesystem path of the configuration file
                to be loaded.
        """

        self.configuration = load.configuration(filepath)
        try:
            self.installed = load.installed(self.configuration)
        except validate.SemanticError:
            pass
        try:
            self.available = load.available(self.configuration)
        except validate.SemanticError:
            pass

    def _install(self, package, filepath, flags = []):
        """ Performs a low-level package installation.

        Parameters
            package
                the package to be installed.
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

        db = self.configuration.db()
        architecture = package.architecture
        name = package.name
        version = package.version

        required = [
            db+'installed/',
            db+'installed/'+name,
            db+'installed/'+name+'/'+version
        ]
        for each in required:
            try:
                mkdir(each)
            except OSError:
                pass

        if package in self.installed:
            message.warning("'{0}' is already installed.".format(package))
            raise InstallError
        else:
            try:
                mkdir(db+'installed/'+name+'/'+version+'/'+architecture)
            except OSError:
                message.warning("failed to create internal directory while installing '{0}'.".format(package))
                raise InstallError

        try:
            chdir(db+'installed/'+name+'/'+version+'/'+architecture)
        except OSError:
            message.warning("could not access the directory belonging to package '{0}'.".format(package))
            raise InstallError

        for flag in flags:
            package.add_flag(flag)

        sha1 = package.has_checksum('sha1')
        if sha1:
            if not filepath:
                message.warning("missing archive filepath for non-metapackage '{0}'.".format(package))
                raise InstallError

            if not checksum.sha1(filepath, sha1):
                message.warning("inconsistent archive for package '{0}'.".format(package))
                try:
                    rmtree(db+'installed/'+name+'/'+version+'/'+architecture)
                except OSError:
                    raise
                raise InstallError

            files = archive.getfiles(filepath)
            if not files:
                try:
                    rmtree(db+'installed/'+name+'/'+version+'/'+architecture)
                except OSError:
                    raise
                raise InstallError

            try:
                files_dump = open('files', 'w')
                for each in files:
                    files_dump.write(each+'\n')
            except IOError:
                raise InstallError
            files_dump.close()

            if not archive.extract(filepath, self.configuration.root()):
                try:
                    rmtree(db+'installed/'+name+'/'+version+'/'+architecture)
                except OSError:
                    raise
                raise InstallError

        try:
            if not dump.package(package, 'metadata.yml'):
                message.warning("failed to write metadata.yml for package '{0}'.".format(package))
                raise InstallError
        except IOError:
            raise

        self.installed.add(package)
        return True

    def _uninstall(self, package):
        """ Performs a low-level package uninstallation.

        Parameters
            package
                the package to be uninstalled.
        Raises
            UninstallError
                if any error occurs during the uninstallation.
        Returns
            True
                if the uninstallation was successfully completed.
        """

        db = self.configuration.db()
        root = self.configuration.root()
        architecture = package.architecture
        name = package.name
        version = package.version

        if package not in self.installed:
            message.warning("package '{0}' is not installed.".format(package))
            raise UninstallError

        try:
            chdir(db+'installed/'+name+'/'+version+'/'+architecture)
        except OSError:
            message.warning("could not access the directory belonging to package '{0}'.".format(package))
            raise UninstallError

        files = []
        try:
            handle = open('files')
        except IOError:
            pass
        else:
            files = handle.read().splitlines()
            handle.close()

        for each in files:
            if not access(root+each, W_OK):
                message.warning("cannot remove file '{0}' from package '{1}'.".format(root+each, package))
                raise UninstallError

        must_remove = [
            db+'installed/'+name+'/'+version+'/'+architecture+'/metadata.yml',
            db+'installed/'+name+'/'+version+'/'+architecture+'/files',
            db+'installed/'+name+'/'+version+'/'+architecture
        ]

        for each in must_remove:
            if isfile(each) or isdir(each):
                if not access(each, W_OK):
                    message.warning("cannot remove file '{0}'.".format(each))
                    raise UninstallError

        for each in files:
            if isdir(root+each):
                rmdir(root+each)
            elif isfile(root+each):
                remove(root+each)
        for each in must_remove:
            if isdir(each):
                rmdir(each)
            elif isfile(each):
                remove(each)

        try_to_remove = [
            db+'installed/'+name+'/'+version,
            db+'installed/'+name
        ]
        for each in try_to_remove:
            try:
                rmdir(each)
            except OSError:
                break

        self.installed.remove(package)
        return True

    def install(self, units):
        """ Installs a collection of units.
        Resolves dependencies, handles conflicts and checks
        for disabled CPU architectures.

        Parameters
            units
                iterable having all units to be installed.
        Raises
            BrokenDependency
                if a dependency could not be resolved.
            Conflict
                if a conflict was found between two units.
            UnitNotAllowed
                if at least one of the units targeted for installation
                is not able to be installed due to its CPU architecture
                being disabled.
        Returns
            list
                having all Package units to be installed.
        """

        to_install = Set()

        # Remove all already installed units from the list
        for unit in to_install:
            if unit in self.installed:
                message.simple("'{0}' is already installed. Ignoring...".format(unit))
                to_install.remove(unit)

        # Dependency resolution
        for unit in units:
            if isinstance(unit, Package):
                unit.add_temporary_flag('installed-by-user')
            to_install.add(unit)
            try:
                unit.target_for_installation(self.installed, self.available, to_install)
            except BrokenDependency:
                raise

        # Remove all already installed units from the list a second time
        for unit in to_install:
            if unit in self.installed:
                message.simple("'{0}' is already installed. Ignoring...".format(unit))
                to_install.remove(unit)

        # Check if any of the units is not allowed due to one their CPU
        # architectures not being enabled
        for unit in to_install:
            if not self.configuration.is_unit_allowed(unit):
                message.simple("'{0}' is not allowed to be installed since its architecture is not currently enabled.".format(unit))
                raise UnitNotAllowed

        # Check for conflicts
        for unit in to_install:
            if isinstance(unit, Incompatible):
                try:
                    unit.check_for_conflicts(self.installed, to_install)
                except Conflict:
                    raise

        # Remove Groups and VirtualPackages
        to_install = list(to_install)
        for unit in to_install:
            if isinstance(unit, (Group, VirtualPackage)):
                to_install.remove(unit)

        return to_install

    def uninstall(self, units):
        really_targeted = Set()
        already_targeted = Set()
        units = Set(units)

        # Ignore units which are not installed.
        for unit in units:
            if unit not in self.installed:
                message.simple("'{0}' is not installed. Ignoring...".format(unit))
                units.remove(unit)

        # Target all units that were installed purely as dependencies
        # and are no longer needed
        for unit in units:
            unit.target_for_uninstallation(units, really_targeted, already_targeted, self.installed)

        return really_targeted

    def download(self, packages):
        """ Download packages.

        Parameters
            packages
                an iterable having the packages to be downloaded.
        Raises
            DownloadError
                in case of failure.
        Returns
            True
                in case all specified packages have been successfully downloaded.
        """

        grouped_packages = {}

        for package in packages:
            try:
                grouped_packages[package.repository].append(package)
            except KeyError:
                grouped_packages[package.repository] = []
                grouped_packages[package.repository].append(package)

        for repository_name in grouped_packages.iterkeys():
            try:
                repository = self.configuration.repositories()[repository_name]
            except KeyError:
                raise DownloadError

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
                        self.configuration.db()+'/available',
                        self.configuration.db()+'/available/'+repository_name,
                        self.configuration.db()+'/available/'+repository_name+'/cache',
                        self.configuration.db()+'/available/'+repository_name+'/cache/'+n,
                        self.configuration.db()+'/available/'+repository_name+'/cache/'+n+'/'+v,
                        self.configuration.db()+'/available/'+repository_name+'/cache/'+n+'/'+v+'/'+a
                    ]

                    for directory in directories:
                        try:
                            mkdir(directory)
                        except OSError:
                            pass

                    try:
                        chdir(self.configuration.db()+'/available/'+package.repository+'/cache/'+n+'/'+v+'/'+a)
                    except OSError:
                        raise DownloadError

                    if not isfile('package.tar.gz'):
                        handler = repository['handler']
                        target = "{0}/{1}/{2}/{3}/package.tar.gz".format(repository['target'], n, v, a)
                        if system(handler+' '+target) != 0:
                            raise DownloadError

            try:
                environment.purge(repository['env'].keys())
            except environment.EnvironmentError:
                message.warning("could not purge the environment variables associated to the repository '{0}'!".format(package.repository))
            except KeyError:
                pass

        return True

    def search(self, term, set):
        """ Search for units.

        Parameters
            term
                string to be searched for.
        Raises
            ValueError
                if no units could be found matching the specified term.
        Returns
            True
                if the search was successful, and one or more units were found
                matching the specified criteria.
        """

        try:
            found = set.search(term)
        except ValueError:
            message.simple("Nothing found while search for the term '{0}'.".format(term))
            raise
        else:
            for each in found:
                message.simple("{0}".format(each))
            return True

    def clear(self, cache):
        """ Clears the local cache and repositories' metadata.

        Parameters
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
            path = self.configuration.db()+'/available/*'
        else:
            path = self.configuration.db()+'/available/*/*.yml'

        for each in glob(path):
            try:
                if isdir(each):
                    rmtree(each)
                else:
                    remove(each)
            except OSError:
                raise ClearError

        self.available = load.available(self.configuration)
        return True

    def sync(self):
        """ Synchronises enabled repositories from a Craft self.configuration.

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
            self.clear(False)
        except ClearError:
            raise

        for name in self.configuration.repositories().iterkeys():
            repository = self.configuration.repositories()[name]
            try:
                mkdir(self.configuration.db()+'available')
            except OSError:
                pass

            try:
                mkdir(self.configuration.db()+'available/'+name)
            except OSError:
                pass

            try:
                chdir(self.configuration.db()+'available/'+name)
            except OSError:
                raise SyncError

            try:
                environment.merge(repository['env'])
            except environment.EnvironmentError:
                message.warning("could not merge the environment variables associated to the repository '{0}'!".format(name))
            except KeyError:
                pass

            handler = repository['handler']
            for arch in self.configuration.architectures():
                target = repository['target']+'/'+arch+'.yml'
                if system(handler+' '+target) != 0:
                    message.warning("could not synchronise architecture '{0}' from repository '{1}'!".format(arch, name))

            try:
                environment.purge(repository['env'].keys())
            except environment.EnvironmentError:
                message.warning("could not purge the environment variables associated to the repository '{0}'!".format(name))
            except KeyError:
                pass

        self.available = load.available(self.configuration)
        return True
