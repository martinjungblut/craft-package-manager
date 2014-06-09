# -*- coding: utf8 -*-
""" Handle the unit relationship DSL. """

# Standard library imports
import re

def parse(other):
    """ Parses a unit relationship.

    Parameters
        other
            string describing the other end of a unit relationship.
    Returns
        list
            having the parsed fragments of the other end's description.
        False
            in case other is not valid.
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
            
    matches = re.findall("([\w\(\))]+)\s*(>{0,1}<{0,1}={0,1})\s*([a-za-z0-9\.]*)", other.lower())
    if matches:
        matches = list(matches[0])
        if not matches[1] and matches[2]:
            matches[1] = "="
        return matches
    else:
        return False
