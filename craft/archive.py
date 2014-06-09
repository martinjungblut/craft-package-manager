""" Interface for managing package archives. """

# Standard library imports
from tarfile import open as archive_open

def getfiles(filepath):
    """ Get all files from a package file as a list,
    ignoring special control files.

    Parameters
        filepath
            package archive for the files list to be retrieved from.
    Returns
        list
            having the package's archive's files' names.
        False
            if an IOError occurred during any of the operations.
    """

    controlfiles = [
        '.', './.craft', './.craft/postinst',
        './.craft/postrm', './.craft/preinst', './.craft/prerm'
    ]

    try:
        handle = archive_open(filepath)
    except IOError:
        return False

    files = handle.getnames()
    handle.close()

    try:
        for controlfile in controlfiles:
            files.remove(controlfile)
    except ValueError:
        pass

    return reversed(files)

def extract(filepath, destination):
    """ Extract a package file to a specified destination.

    Returns
        True
            if the package file was successfully extracted.
        False
            if the package file could not be extracted.
    """
    try:
        handle = archive_open(filepath)
        handle.extractall(destination)
    except IOError:
        return False
    finally:
        handle.close()

    return True
