""" Errors and warnings. """

from sys import exit as sys_exit

def fatal(message, code):
    """ Informs the user a fatal error has occurred.
    message is printed to the screen
    code is returned as the system's exit status. """
    print("Fatal error: "+message)
    sys_exit(code)

def warning(message):
    """ Informs the user about an unexpected event. """
    print("Warning: "+message)
