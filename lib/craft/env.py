""" Environment functions. """

# Standard library imports
from os import putenv, unsetenv

def merge(env):
    """ Merges variables to the current environment.

    Parameters
        env
            dictionary containing the variables' names
            and values to be merged to the current environment.
    Raises
        TypeError
            if env is not a dict.
    Returns
        True
            if all variables were successfully merged
            to the environment.
        False
            immediately when a variable fails to be merged
            to the environment.
    """

    if not isinstance(env, dict):
        raise TypeError
    try:
        for variable, value in env.items():
            putenv(variable, value)
        return True
    except:
        return False

def purge(env):
    """ Purges variables from the current environment.

    Parameters
        env
            list containing the variables' names
            to be purged from the current environment.
    Raises
        TypeError
            if env is not a list.
    Returns
        True
            if all variables were successfully purged
            from the environment.
        False
            immediately when a variable fails to be purged
            from the environment.
    """

    if not isinstance(env, list):
        raise TypeError
    try:
        for variable in env:
            unsetenv(variable)
        return True
    except:
        return False
