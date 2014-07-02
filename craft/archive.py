""" Manage archives. """

# Standard library imports
from tarfile import open as archive_open

def getfiles(filepath):
    """ Retrieve all files from an archive as a list.

    Parameters
        filepath
            archive for the files list to be retrieved from.
    Returns
        list
            having the archive's files' names.
        False
            if an IOError occurred during any of the operations.
    """

    try:
        handle = archive_open(filepath)
    except IOError:
        return False
    else:
        files = handle.getnames()
        handle.close()

    return reversed(files)

def extract(filepath, destination):
    """ Extract an archive to a specific destination.

    Parameters
        filepath
            archive for the files to be extracted from.
        destination
            filesystem destination for the archive to be extracted to. 
    Returns
        True
            if the archive was successfully extracted.
        False
            if the archive could not be extracted.
    """

    try:
        handle = archive_open(filepath)
    except IOError:
        return False
    else:
        handle.extractall(destination)
        handle.close()

    return True
