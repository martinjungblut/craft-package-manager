""" Actions. """

# Standard library imports
from glob import glob
from os import system, mkdir, chdir
from shutil import rmtree

# Craft imports
import load
import errors
import sets

def highmerge(configuration, unit_names):
    try:
        world = load.world(configuration)
    except load.WorldError:
        errors.fatal("There are no enabled repositories.")
    units = []
    for repository in world.sets:
        for unit_name in unit_names:
            try:
                units = units + repository.search(unit_name, configuration)
            except sets.NoMatchFound:
                pass
    return units

def unmerge(unit_names):
    pass

def download(units):
    pass

def lowmerge(units):
    pass

def clear(configuration):
    for directory in glob(configuration.db+'/world/*'):
        try:
            rmtree(directory)
        except OSError:
            pass

def sync(configuration):
    clear(configuration)
    for name in configuration.repositories.iterkeys():
        repository = configuration.repositories[name]
        try:
            mkdir(configuration.db+'/world')
            mkdir(configuration.db+'/world/'+name)
        except OSError:
            pass
        chdir(configuration.db+'/world/'+name)
        target = repository['target']+'/'+name+'/metadata.yml'
        handler = repository['handler']
        system(handler+' '+target)
