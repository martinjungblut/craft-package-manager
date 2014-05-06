""" General utilities. """

import yaml

class YAMLError(Exception):
    pass

def load_yaml(file_path):
    """ Opens a YAML file, parses it and returns its data. """
    file_handle = open(file_path)
    try:
        data = yaml.load(file_handle)
    except:
        raise YAMLError
    file_handle.close()
    return data
