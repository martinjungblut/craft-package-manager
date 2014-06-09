""" Dump units to YAML. """

# Third-party imports
import yaml

def package(package, filepath):
    """ Dumps a package unit to an YAML file.

    Parameters
        package
            Package object to be dumped.
        filepath
            path of the file for the object to be dumped in.
    Raises
        IOError
            in case it is not possible to write to such file.
    Returns
        True
            if the package was successfully dumped.
    """

    outer = {}
    outer[package.name] = {}
    outer[package.name][package.version] = {}
    inner = {}
    inner['hashes'] = package.hashes
    inner['depends'] = package.dependencies
    inner['conflicts'] = package.conflicts
    inner['replaces'] = package.replaces
    inner['provides'] = package.provides
    inner['groups'] = package.groups
    inner['flags'] = package.flags

    for each in inner.iterkeys():
        if len(inner[each]) == 0:
            inner[each] = None

    inner['information'] = {}
    inner['information']['maintainers'] = package.maintainers
    inner['information']['tags'] = package.tags
    inner['information']['misc'] = package.misc

    for each in inner['information'].iterkeys():
        if len(inner['information'][each]) == 0:
            inner['information'][each] = None

    inner['files'] = {}
    inner['files']['static'] = package.files['static']

    outer[package.name][package.version][package.architecture] = inner

    try:
        handle = open(filepath, 'w')
        yaml.dump(outer, handle, default_flow_style=False)
    except IOError:
        raise
    handle.close()

    return True
