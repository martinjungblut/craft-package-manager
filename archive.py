#!/usr/bin/python
# -*- coding: utf-8 -*-

from tarfile import open as tarfile_open

# GZ is being used for now, until it is decided how we're going to add proper XZ/LZMA support to Python 2.X.
readmode = "r|gz"

# Get all files from a package file as a list, ignoring special control files.
def getfiles(filename, controlfiles = ['.','./.craft','./.craft/postinst','./.craft/postrm','./.craft/preinst','./.craft/prerm']):
    try:
        handle = tarfile_open(filename, readmode)
        files = handle.getnames()
        try:
            for controlfile in controlfiles:
                files.remove(controlfile)
        except:
            pass
        handle.close()
        return files
    except:
        try:
            handle.close()
        except:
            pass
        return False

# Uncompress a package file to a specified path.
def uncompress(filename, path="."):
    try:
        fh = tarfile_open(filename, readmode)
        fh.extractall(path)
        fh.close()
        return True
    except:
        try:
            fh.close()
        except:
            pass
    return False
