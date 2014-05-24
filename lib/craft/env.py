""" Environment functions. """

def merge(env):
    """
    Merges variables to the current environment.

    Parameters
        env: dictionary containing the variables' names
        and values to be merged to the current environment.
    Raises
        TypeError: if env is not a dict.
    Returns
        True: if all variables were successfully merged
        to the environment.
        False: immediately when a variable fails to be merged
        to the environment.
    """

    if not isinstance(env, dict):
        raise TypeError
    try:
        for variable, value in env.items():
            os.putenv(variable, value)
        return True
    except:
        return False

def purge(env):
    """
    Purges variables from the current environment.

    Parameters
        env: dictionary containing the variables' names
        and values to be purged from the current environment.
        Note that the values themselves are irrelevant here, since only
        the env's keys will be used for purging.
    Raises
        TypeError: if env is not a dict.
    Returns
        True: if all variables were successfully purged
        from the environment.
        False: immediately when a variable fails to be purged
        from the environment.
    """

    if not isinstance(env, dict):
        raise TypeError
    try:
        for variable, value in env.items():
            os.unsetenv(variable)
        return True
    except:
        return False
