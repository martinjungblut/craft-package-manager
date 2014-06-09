""" Handle errors and warnings. """

# Standard library imports
from sys import exit as sys_exit
from time import localtime

def _isotime():
    """ Retrieve the current time as a string,
    formatted according to the ISO-8601 standard. """

    now = list(localtime()[:-3])

    for each in range(1, len(now)):
        if now[each] < 10:
            now[each] = '0'+str(now[each])

    return '{0}/{1}/{2} {3}:{4}:{5}'.format(now[0], now[1], now[2], now[3], now[4], now[5])

def fatal(message, status):
    """ Informs the user a fatal error has occurred.

    Paramaters
        message
            message to be printed before aborting.
        status
            returned as the system's exit status.
    """

    print('\033[91m'+_isotime()+' Fatal error: '+message+'\033[0m')
    sys_exit(status)

def warning(message):
    """ Informs the user about an unexpected event.

    Paramaters
        message
            the event's description.
    """

    print('\033[93m'+_isotime()+' Warning: '+message+'\033[0m')
