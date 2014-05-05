from yaml import load as yaml_load
from os import listdir as os_listdir

try:
    with open('config.yml') as handle:
        config = yaml_load(handle)
        handle.close()
    del(handle)
except IOError:
    exit("Fatal error: Could not find config.yml!")

repositories = {}
try:
    for directory in os_listdir(config['fakedb']+'/repositories/'):
        try:
            with open(config['fakedb']+'/repositories/'+directory+'/metadata.yml') as handle:
                repositories[directory] = yaml_load(handle)
                handle.close()
        except IOError:
            print("Warning: Missing 'metadata.yml' for repository '{0}'!".format(directory))
            pass
except OSError:
    exit("Fatal error! Repositories directory not found!")
