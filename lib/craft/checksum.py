""" File checksum verification. """

# Standard library imports
import hashlib


def sha1(filepath):
    """ Calculates the SHA-1 checksum of a file.

    Parameters
        filepath
            file to be read.
    Raises
        IOError
            if the file could not be read.
    Returns
        string
            the file's SHA-1 checksum.
    """

    hasher = hashlib.sha1()
    blocksize = 65536

    try:
        handle = open(filepath, 'rb')
    except IOError:
        raise

    buf = handle.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = handle.read(blocksize)

    handle.close()

    return hasher.hexdigest()
