""" Actions. """

# Standard library imports
from glob import glob
from os import system, mkdir, chdir
from shutil import rmtree

# Third-party imports
from yaml import dump

# Craft imports
import load
import sets
import env
import error
import archive
from units import Package
from configuration import Configuration

class InstallError(Exception):
    pass

def install(configuration, unit_names):
    try:
        world = load.world(configuration)
    except load.WorldError:
        raise InstallError
    packages = set()
    for repository in world.sets:
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
    if not isinstance(package, Package):
        raise TypeError
    elif not isinstance(configuration, Configuration):
        raise TypeError
    n = package.name
    v = package.version
    a = package.architecture
    try:
        mkdir(configuration.db+'/selected/')
        mkdir(configuration.db+'/selected/'+n)
        mkdir(configuration.db+'/selected/'+n+'/'+v)
        mkdir(configuration.db+'/selected/'+n+'/'+v+'/'+a)
    except OSError:
        pass
    try:
        chdir(configuration.db+'/selected/'+n+'/'+v+'/'+a)
    except OSError:
        raise InstallError
    files = archive.getfiles(filepath)
    if not files:
        raise InstallError
    try:
        files_dump = open('files.yml', 'w')
        dump(files, files_dump, default_flow_style = False)
    except IOError:
        raise InstallError
    finally:
        files_dump.close()
    if not archive.extract(filepath, configuration.root):
        raise InstallError
    return True

def unmerge(unit_names):
    pass

def download(units):
    pass

def ClearError(Exception):
    pass

def clear(configuration):
    """ Clear local cache and repositories' metadata.

    Raises
        ClearError if of failure.
    """

    for directory in glob(configuration.db+'/world/*'):
        try:
            rmtree(directory)
        except OSError:
            raise ClearError

class SyncError(Exception):
    pass

def sync(configuration):
    """
    Synchronises enabled repositories from a Craft configuration.

    Parameters
        configuration: a Configuration object.
    Raises
        SyncError: in case of failure related to the actual
        synchronisation.
        ClearError: if the internal clear() call fails and the previously set
        local repository cache is not properly cleared up prior to the
        actual synchronisation.
    Returns
        True: if all repositories were successfully synchronised.
    """

    try:
        clear(configuration)
    except ClearError:
        raise
    for name in configuration.repositories.iterkeys():
        repository = configuration.repositories[name]
        try:
            mkdir(configuration.db+'/world')
        except OSError:
            pass
        try:
            mkdir(configuration.db+'/world/'+name)
            chdir(configuration.db+'/world/'+name)
        except OSError:
            raise SyncError
        target = repository['target']+'/metadata.yml'
        handler = repository['handler']
        if 'env' in repository:
            print(repository['env'])
            if not env.merge(repository['env']):
                error.warning("could not merge the environment variables associated to the repository '{0}'!".format(name))
        system(handler+' '+target)
        if 'env' in repository:
            if not env.purge(repository['env']):
                error.warning("could not purge the environment variables associated to the repository '{0}'!".format(name))

    return True
