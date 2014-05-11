""" Interface for handling errors and warnings. """

# Standard library imports
from sys import exit as sys_exit

def fatal(message, status):
    """ Informs the user a fatal error has occurred.
    message is printed to the screen
    status is returned as the system's exit status. """
    print("Fatal error: "+message)
    sys_exit(status)

def warning(message):
    """ Informs the user about an unexpected event. """
    print("Warning: "+message)
