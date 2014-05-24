""" Actions. """

# Standard library imports
from glob import glob
from os import system, mkdir, chdir
from shutil import rmtree

# Craft imports
import load
import sets
import env

class InstallError(Exception):
    pass

def install(configuration, unit_names):
    try:
        world = load.world(configuration)
    except load.WorldError:
        raise InstallError
    units = []
    for repository in world.sets:
        for unit_name in unit_names:
            try:
                units = units + repository.search(configuration, unit_name)
            except sets.NoMatchFound:
                pass
    return units

def unmerge(unit_names):
    pass

def download(units):
    pass

def _install(units):
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
                raise SyncError
        system(handler+' '+target)
        if 'env' in repository:
            if not env.purge(repository['env']):
                raise SyncError

    return True
