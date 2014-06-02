""" Environment functions. """

# Standard library imports
from os import putenv, unsetenv

class EnvError(Exception):
    """ Raised if there is an error in an environment-related operation. """
    pass

def merge(env):
    """ Merges variables to the current environment.

    Parameters
        env
            dictionary containing the variables' names
            and values to be merged to the current environment.
    Raises
        EnvError
            if the specified variables could not be
            merged to the environment.
    """

    try:
        for variable, value in env.items():
            putenv(variable, value)
    except:
        raise EnvError

def purge(env):
    """ Purges variables from the current environment.

    Parameters
        env
            list containing the variables' names
            to be purged from the current environment.
    Raises
        EnvError
            if the specified variables could not be
            purged from the environment.
    """

    try:
        for variable in env:
            unsetenv(variable)
    except:
        raise EnvError
