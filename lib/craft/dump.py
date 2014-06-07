""" Dump units to YAML. """

# Third-party imports
import yaml

def package(pkg, filepath):
    """ Dumps a pkg unit to an YAML file.

    Parameters
        pkg
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

    container = {}
    container[pkg.name] = {}
    container[pkg.name][pkg.version] = {}

    unit = {}
    unit['hashes'] = pkg.hashes
    unit['depends'] = pkg.dependencies
    unit['conflicts'] = pkg.conflicts
    unit['replaces'] = pkg.replaces
    unit['provides'] = pkg.provides
    unit['groups'] = pkg.groups
    unit['flags'] = pkg.flags

    for each in unit.iterkeys():
        if len(unit[each]) == 0:
            unit[each] = None

    unit['information'] = {}
    unit['information']['maintainers'] = pkg.maintainers
    unit['information']['tags'] = pkg.tags
    unit['information']['misc'] = pkg.misc

    for each in unit['information'].iterkeys():
        if len(unit['information'][each]) == 0:
            unit['information'][each] = None

    unit['files'] = {}
    unit['files']['static'] = pkg.files['static']

    container[pkg.name][pkg.version][pkg.architecture] = unit

    try:
        handle = open(filepath, 'w')
    except IOError:
        raise

    yaml.dump(container, handle, default_flow_style=False)
    handle.close()
    return True
