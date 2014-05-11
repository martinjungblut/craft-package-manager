""" Interface for loading Craft-related files. """

# Third-party imports
import yaml

# Craft imports
import validate
from configuration import Configuration
from repository import Repository
from units import Package, MetaPackage

class YAMLError(Exception):
    """ Abstracts yaml.YAMLError in a native Craft exception. """
    pass

def yaml(file_path):
    """ Opens a YAML file, parses it and returns its data.
    Raises YAMLError in case the file is not a valid YAML file.
    Raises IOError in case the file could not be read. """
    try:
        file_handle = open(file_path)
        data = yaml.load(file_handle)
        return data
    except yaml.YAMLError:
        raise YAMLError
    finally:
        file_handle.close()

def repository(file_path):
    """ Opens a repository definition file, parses it,
    validates it and returns a Repository object.
    Raises IOError in case the file could not be read.
    Raises YAMLError in case the file is not a valid YAML file.
    Raises RepositoryError in case the file is semantically invalid. """
    definition = yaml(file_path)
    validate.repository(definition)
    return Repository(definition)

def configuration(file_path):
    """ Opens a configuration file, parses it,
    validates it and returns a Configuration object.
    Raises IOError in case the file could not be read.
    Raises YAMLError in case the file is not a valid YAML file.
    Raises ConfigurationError in case the file is semantically invalid. """
    definition = yaml(file_path)
    validate.configuration(definition)
    return Configuration(definition)
