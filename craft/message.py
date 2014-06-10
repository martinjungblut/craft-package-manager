""" Send messages to the user. """

# Standard library imports
from time import localtime

def _isotime():
    """ Retrieve the current time as a string,
    formatted according to the ISO-8601 standard. """

    now = list(localtime()[:-3])

    for each in range(1, len(now)):
        if now[each] < 10:
            now[each] = '0'+str(now[each])

    return '{0}/{1}/{2} {3}:{4}:{5}'.format(now[0], now[1], now[2], now[3], now[4], now[5])

def warning(message):
    """ Informs the user about an unexpected event.

    Paramaters
        message
            the event's description.
    """

    print('\033[93m'+_isotime()+' Warning: '+message+'\033[0m')

def simple(message):
    """ Display a simple, uncoloured message to the user.

    Paramaters
        message
            string to be displayed.
    """

    print(_isotime()+message)
