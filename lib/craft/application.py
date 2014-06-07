""" Actions. """

# Standard library imports
from glob import glob
from os import system, mkdir, chdir, rmdir, remove, access, W_OK
from os.path import isfile, isdir
from shutil import rmtree

# Third-party imports
import yaml

# Craft imports
import archive
import checksum
import dump
import env
import error
import load

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

class Craft(object):
    def __init__(self):
        self.configuration = load.configuration('config.yml')
        self.installed = load.installed(self.configuration)
        self.available = load.available(self.configuration)

    def _install(self, package, filepath):
        """ Performs a low-level package installation.

        Parameters
            package
                the package to be installed.
            filepath
                the package's archive's absolute path.
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

        db = self.configuration.db
        architecture = package.architecture
        name = package.name
        version = package.version

        required = [
            db+'/installed/',
            db+'/installed/'+name,
            db+'/installed/'+name+'/'+version
        ]
        for each in required:
            try:
                mkdir(each)
            except OSError:
                pass

        if package not in self.installed:
            try:
                mkdir(db+'/installed/'+name+'/'+version+'/'+architecture)
            except OSError:
                error.warning("Failed to create internal directory while installing '{0}'.".format(package))
                raise InstallError
        else:
            error.warning("'{0}' seems to be already installed.".format(package))
            raise InstallError

        try:
            chdir(db+'/installed/'+name+'/'+version+'/'+architecture)
        except OSError:
            error.warning("Could not access the directory belonging to package '{0}'.".format(package))
            raise InstallError

        for hash in package.hashes.iterkeys():
            if hash == 'sha1':
                if not checksum.sha1(filepath, package.hashes[hash]):
                    error.warning("Inconsistent archive for package '{0}'.".format(package))
                    try:
                        rmtree(db+'/installed/'+name+'/'+version+'/'+architecture)
                    except OSError:
                        raise
                    raise InstallError
            else:
                error.warning("'{0}' has an unsupported archive checksum type: {1}. Ignoring...".format(package, hash))

        files = archive.getfiles(filepath)
        if not files:
            try:
                rmtree(db+'/installed/'+name+'/'+version+'/'+architecture)
            except OSError:
                raise
            raise InstallError

        try:
            files_dump = open('files', 'w')
            for each in files:
                files_dump.write(each+'\n')
        except IOError:
            raise InstallError
        finally:
            files_dump.close()

        try:
            if not dump.package(package, 'metadata.yml'):
                error.warning("Failed to write metadata.yml for package '{0}'.".format(package))
                raise InstallError
        except IOError:
            raise

        if not archive.extract(filepath, self.configuration.root):
            try:
                rmtree(db+'/installed/'+name+'/'+version+'/'+architecture)
            except OSError:
                raise
            raise InstallError

        self.installed.append(package)

        return True

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
                repository = self.configuration.repositories[repository_name]
            except KeyError:
                raise DownloadError

            try:
                env.merge(repository['env'])
            except env.EnvError:
                error.warning("could not merge the environment variables associated to the repository '{0}'!".format(repository_name))
            except KeyError:
                pass

            for package in grouped_packages[repository_name]:

                if len(package.hashes) > 0:
                    n = package.name
                    v = package.version
                    a = package.architecture

                    directories = [
                        self.configuration.db+'/available',
                        self.configuration.db+'/available/'+repository_name,
                        self.configuration.db+'/available/'+repository_name+'/cache',
                        self.configuration.db+'/available/'+repository_name+'/cache/'+n,
                        self.configuration.db+'/available/'+repository_name+'/cache/'+n+'/'+v,
                        self.configuration.db+'/available/'+repository_name+'/cache/'+n+'/'+v+'/'+a
                    ]

                    for directory in directories:
                        try:
                            mkdir(directory)
                        except OSError:
                            pass

                    try:
                        chdir(self.configuration.db+'/available/'+package.repository+'/cache/'+n+'/'+v+'/'+a)
                    except OSError:
                        raise DownloadError

                    if not isfile('package.tar.gz'):
                        handler = repository['handler']
                        target = "{0}/{1}/{2}/{3}/package.tar.gz".format(repository['target'], n, v, a)
                        if system(handler+' '+target) != 0:
                            raise DownloadError

            try:
                env.purge(repository['env'].keys())
            except env.EnvError:
                error.warning("could not purge the environment variables associated to the repository '{0}'!".format(package.repository))
            except KeyError:
                pass

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

        if package not in self.installed:
            error.warning("Package '{0}' is not installed.")
            raise UninstallError

        db = self.configuration.db
        root = self.configuration.root
        architecture = package.architecture
        name = package.name
        version = package.version

        try:
            chdir(db+'/installed/'+name+'/'+version+'/'+architecture)
        except OSError:
            error.warning("Could not access the directory belonging to package '{0}'.".format(package))
            raise UninstallError

        try:
            handle = open('files')
        except IOError:
            error.warning("Could not read the files list belonging to package '{0}'.".format(package))
            raise UninstallError

        files = handle.read().splitlines()
        handle.close()

        for each in files:
            if not access(root+each, W_OK):
                error.warning("Can not remove file '{0}' from package '{1}'.".format(root+each, package))
                raise UninstallError

        paths = [
            db+'/installed/'+name+'/'+version+'/'+architecture+'/metadata.yml',
            db+'/installed/'+name+'/'+version+'/'+architecture+'/files',
            db+'/installed/'+name+'/'+version+'/'+architecture
        ]

        for each in paths:
            if not access(each, W_OK):
                error.warning("Can not remove file '{0}'.".format(each))
                raise UninstallError

        for each in files:
            if isdir(root+each):
                rmdir(root+each)
            else:
                remove(root+each)
        for each in paths:
            if isdir(each):
                rmdir(each)
            else:
                remove(each)

        self.installed.remove(package)

        return True

    def clear(self):
        """ Clear local cache and repositories' metadata.

        Raises
            ClearError
                in case of failure.
        Returns
            True
                in case the local cache has been successfully cleared.
        """

        for directory in glob(self.configuration.db+'/available/*'):
            try:
                rmtree(directory)
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
            self.clear()
        except ClearError:
            raise

        for name in self.configuration.repositories.iterkeys():
            repository = self.configuration.repositories[name]
            try:
                mkdir(self.configuration.db+'/available')
            except OSError:
                pass
            try:
                mkdir(self.configuration.db+'/available/'+name)
                chdir(self.configuration.db+'/available/'+name)
            except OSError:
                raise SyncError

            try:
                env.merge(repository['env'])
            except env.EnvError:
                error.warning("could not merge the environment variables associated to the repository '{0}'!".format(name))
            except KeyError:
                pass

            handler = repository['handler']
            for arch in self.configuration.architectures:
                target = repository['target']+'/'+arch+'.yml'
                if system(handler+' '+target) != 0:
                    error.warning("could not synchronise architecture '{0}' from repository '{1}'!".format(arch, name))

            try:
                env.purge(repository['env'].keys())
            except env.EnvError:
                error.warning("could not purge the environment variables associated to the repository '{0}'!".format(name))
            except KeyError:
                pass

        self.available = load.available(self.configuration)

        return True
