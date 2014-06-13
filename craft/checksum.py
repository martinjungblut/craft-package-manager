""" File checksum verification. """

# Standard library imports
import hashlib

def sha1(filepath, expected):
    """ Calculates and verifies the SHA-1 checksum of a file's
    contents.

    Parameters
        filepath
            file to be read.
        expected
            the expected SHA-1 checksum.
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
    else:
        buf = handle.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = handle.read(blocksize)
        handle.close()

    if hasher.hexdigest() == expected:
        return True
    else:
        return False
