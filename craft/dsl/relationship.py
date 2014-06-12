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
        >>> parse('python >= 2.7.7')
        ['python', '>=', '2.7.7']
        >>> parse('python') # No specific version is provided
        ['python', '', '']
        >>> parse('python(i386) < 3') # Multi-architecture relationship
        ['python(i386)', '<', '3']
        >>> parse('python(i386) = 3.12')
        ['python(i386)', '=', '3.12']
        >>> parse('python(i386) 3.12') # Note how the 'equals' idea is implicitly added if not explicitly defined
        ['python(i386)', '=', '3.12']
        >>> parse('€') # Invalid character, ignored
        False
        >>> parse('')
        False
    """

    matches = re.findall("([a-z0-9\-\.:]+)\s*(>{0,1}<{0,1}={0,1})\s*([a-z0-9\-\.]*)", target)
    if matches:
        if "".join(matches[0]) == "".join(target.split()):
            matches = list(matches[0])
            if not matches[1] and matches[2]:
                matches[1] = "="
            return matches
    return False

def multiarch(target):
    """ Checks whether a unit relationship is a multi-architecture one.

    Parameters
        target
            string to be checked.
    Returns
        string
            the architecture's name.
        False
            in case target is invalid, or if the relationship is not
            a multi-architecture one.
    Example
        >>> multiarch('python:amd64')
        'amd64'
        >>> multiarch('python')
        False
        >>> multiarch('')
        False
    """

    try:
        return target.split(':')[1]
    except IndexError:
        return False
