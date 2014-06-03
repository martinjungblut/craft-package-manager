""" Actions. """

# Standard library imports
from glob import glob
from os import system, mkdir, chdir
from os.path import isfile
from shutil import rmtree

# Third-party imports
from yaml import dump

# Craft imports
import archive
import env
import error
import load
import sets

class InstallError(Exception):
    pass

def install(configuration, unit_names):
    try:
        available = load.available(configuration)
    except load.AvailableError:
        raise InstallError
    packages = set()
    for repository in available.sets:
        for unit_name in unit_names:
            try:
                found = repository.search(configuration, unit_name)
                for f in found:
                    packages.add(f)
            except sets.NoMatchFound:
                pass
    print("The following packages are going to be installed: ")
    for package in packages:
        print(package.name)
    return True

def _install(configuration, package, filepath):
    n = package.name
    v = package.version
    a = package.architecture

    try:
        mkdir(configuration.db+'/installed/')
    except OSError:
        pass
    try:
        mkdir(configuration.db+'/installed/'+n)
    except OSError:
        pass
    try:
        mkdir(configuration.db+'/installed/'+n+'/'+v)
    except OSError:
        pass
    try:
        mkdir(configuration.db+'/installed/'+n+'/'+v+'/'+a)
        chdir(configuration.db+'/installed/'+n+'/'+v+'/'+a)
    except OSError:
        raise InstallError

    files = archive.getfiles(filepath)
    if not files:
        raise InstallError
    try:
        files_dump = open('files.yml', 'w')
        dump(files, files_dump, default_flow_style = False)
        metadata_dump = open('metadata.yml', 'w')
        dump(package, metadata_dump, default_flow_style = False)
    except IOError:
        raise InstallError
    finally:
        files_dump.close()
        metadata_dump.close()
    if not archive.extract(filepath, configuration.root):
        raise InstallError

    return True

def unmerge(unit_names):
    pass

class DownloadError(Exception):
    pass

def download(configuration, packages):
    """ Download packages.

    Parameters
        configuration
            a Configuration object having the required data for downloading
            the packages.
        packages
            an iterable having the appropriate Package objects to be downloaded.
    Raises
        DownloadError
            in case of failure.
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
            repository = configuration.repositories[repository_name]
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
                    configuration.db+'/available',
                    configuration.db+'/available/'+repository_name,
                    configuration.db+'/available/'+repository_name+'/cache',
                    configuration.db+'/available/'+repository_name+'/cache/'+n,
                    configuration.db+'/available/'+repository_name+'/cache/'+n+'/'+v,
                    configuration.db+'/available/'+repository_name+'/cache/'+n+'/'+v+'/'+a
                ]

                for directory in directories:
                    try:
                        mkdir(directory)
                    except OSError:
                        pass

                try:
                    chdir(configuration.db+'/available/'+package.repository+'/cache/'+n+'/'+v+'/'+a)
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

def ClearError(Exception):
    pass

def clear(configuration):
    """ Clear local cache and repositories' metadata.

    Raises
        ClearError
            in case of failure.
    """

    for directory in glob(configuration.db+'/available/*'):
        try:
            rmtree(directory)
        except OSError:
            raise ClearError

class SyncError(Exception):
    pass

def sync(configuration):
    """ Synchronises enabled repositories from a Craft configuration.

    Parameters
        configuration
            a Configuration object having the required data for performing
            the synchronisation.
    Raises
        SyncError
            in case of failure related to the actual synchronisation.
        ClearError
            if the internal clear() call fails and the previously set
            local repository cache is not properly cleared up prior to the
            actual synchronisation.
    """

    try:
        clear(configuration)
    except ClearError:
        raise
    for name in configuration.repositories.iterkeys():
        repository = configuration.repositories[name]
        try:
            mkdir(configuration.db+'/available')
        except OSError:
            pass
        try:
            mkdir(configuration.db+'/available/'+name)
            chdir(configuration.db+'/available/'+name)
        except OSError:
            raise SyncError

        try:
            env.merge(repository['env'])
        except env.EnvError:
            error.warning("could not merge the environment variables associated to the repository '{0}'!".format(name))
        except KeyError:
            pass

        handler = repository['handler']
        for arch in configuration.architectures:
            target = repository['target']+'/'+arch+'.yml'
            if system(handler+' '+target) != 0:
                error.warning("could not synchronise architecture '{0}' from repository '{1}'!".format(arch, name))

        try:
            env.purge(repository['env'].keys())
        except env.EnvError:
            error.warning("could not purge the environment variables associated to the repository '{0}'!".format(name))
        except KeyError:
            pass
