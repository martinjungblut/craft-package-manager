# -*- coding: utf8 -*-

""" Handle the unit relationship DSL. """

# Standard library imports
import re

def parse(target):
    """ Parses a unit relationship.

    Parameters
        target
            string describing the other end of a unit relationship.
    Returns
        list
            having the parsed fragments of the other end's description.
        False
            in case target is not valid.
    Example
        >>> parse('python')
        ['python', '']
        >>> parse('python:i386') # Multi-architecture example
        ['python', 'i386']
        >>> parse('€') # Invalid character, ignored
        False
        >>> parse('')
        False
    """

    matches = re.findall('(?=[a-z0-9\-\.]+)(:{0,1}[a-z0-9\-\.]+)?', target)
    if matches:
        return matches[0]
    return False
