""" Dump units to YAML. """

# Third-party imports
import yaml

def package(unit, filepath):
    """ Dumps a unit.unit to an YAML file.

    Parameters
        package
            Package object to be dumped.
        filepath
            absolute filesystem path for the object to be dumped to.
    Raises
        IOError
            in case it is not possible to write to such file.
    Returns
        True
            if the unit.was successfully dumped.
    """

    data = {}
    data[unit.name] = {}
    data[unit.name][unit.version] = {}
    data[unit.name][unit.version][unit.architecture] = unit.data

    try:
        handle = open(filepath, 'w')
    except IOError:
        raise

    yaml.dump(data, handle, default_flow_style=False)
    handle.close()
    return True
