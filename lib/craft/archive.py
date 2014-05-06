""" Provides a uniform interface for managing package archives. """

from tarfile import open as archive_open

def getfiles(filename):
    """ Get all files from a package file as a list,
    ignoring special control files. """
    controlfiles = [
        '.', './.craft', './.craft/postinst',
        './.craft/postrm', './.craft/preinst', './.craft/prerm'
    ]
    try:
        handle = archive_open(filename)
        files = handle.getnames()
        try:
            for controlfile in controlfiles:
                files.remove(controlfile)
        except ValueError:
            pass
        handle.close()
        return files
    except IOError:
        return False

def extract(filename, destination="."):
    """ Extract a package file to a specified destination. """
    try:
        handle = archive_open(filename)
        handle.extractall(destination)
        handle.close()
        return True
    except IOError:
        return False
