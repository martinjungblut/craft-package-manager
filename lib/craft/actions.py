""" Actions. """

# Standard library imports
from glob import glob
from os import system, mkdir, chdir
from shutil import rmtree

# Craft imports
import load
import sets

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

def clear(configuration):
    for directory in glob(configuration.db+'/world/*'):
        try:
            rmtree(directory)
        except OSError:
            pass

class SyncError(Exception):
    pass

def sync(configuration):
    clear(configuration)
    for name in configuration.repositories.iterkeys():
        repository = configuration.repositories[name]
        try:
            mkdir(configuration.db+'/world')
        except OSError:
            pass
        try:
            mkdir(configuration.db+'/world/'+name)
        except OSError:
            raise SyncError
        chdir(configuration.db+'/world/'+name)
        target = repository['target']+'/'+name+'/metadata.yml'
        handler = repository['handler']
        system(handler+' '+target)
