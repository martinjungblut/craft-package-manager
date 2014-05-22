""" Actions. """

# Standard library imports
from glob import glob
from os import system, mkdir, chdir
from shutil import rmtree

def highmerge(unit_names):
    pass

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

class SyncError(Exception):
    pass

def sync(configuration):
    clear(configuration)
    for repository in configuration.repositories.iterkeys():
        try:
            mkdir(configuration.db+'/world')
            mkdir(configuration.db+'/world/'+repository)
        except OSError:
            pass
        chdir(configuration.db+'/world/'+repository)
        target = configuration.repositories[repository]['target']+'/'+repository+'/metadata.yml'
        handler = configuration.repositories[repository]['handler']
        system(handler+' '+target)
