""" Handle the software versioning DSL. """

# Standard library imports
from re import findall

def parse(version):
    """ Parses a specific software versioning string,
    and returns it as a list.

    Parameters
        version
            software versioning string to be parsed.
    Returns
        list
            having all valid fragments of a software version.
        False
            if there are no valid fragments of a software version in
            the provided version.
    Algorithm
        1 Case insensitive regular expression matches letters and numbers.
        2 For each one of the matching groups:
            * Convert it to an integer if possible.
            * Otherwise, convert it to lowercase.
        3 Glue sequential matching groups together.
    """

    matches = findall('([aA-zZ]+|[0-9]+)', str(version))
    if matches:
        for match in matches:
            try:
                matches[matches.index(match)] = int(match)
            except ValueError:
                matches[matches.index(match)] = match.lower()
        str_buffer = ""
        new_matches = []
        for match in matches:
            if isinstance(match, str):
                str_buffer = str_buffer + match
            else:
                if str_buffer:
                    new_matches.append(str_buffer)
                    str_buffer = ""
                new_matches.append(match)
        if str_buffer:
            new_matches.append(str_buffer)
        return new_matches
    else:
        return False

def compare(first, second):
    """ Compares two software version strings.
    Works the same way as C's strcmp.

    Parameters
        first
            software version to be compared to the second parameter.
        second
            software version to be compared to the first parameter.
    Returns
        1
            if first is greater than second.
        -1
            if second is greater than first.
        0
            if first is considered equal to second.
        False
            if neither first nor second are considered valid.

    Algorithm
        1 Parse both versions.
            * If parsing fails or any of the versions is empty,
            return accordingly.
        2 When the versions' length differs:
            * Treat a string remainder as lesser than no remainer.
            * Treat an integer remainer as greater than no remainder.
        3 Return 1 if first is greater than second.
        4 Return -1 if first is lesser than second.
        5 Return 0 if first is equal to second.
    """
    result = False
    f_matches = parse(first)
    s_matches = parse(second)
    if f_matches and s_matches:
        if len(f_matches) > len(s_matches):
            greater_len = len(f_matches)
        else:
            greater_len = len(s_matches)
        for position in range(0, greater_len):
            try:
                if f_matches[position] > s_matches[position]:
                    result = 1
                    break
                elif f_matches[position] < s_matches[position]:
                    result = -1
                    break
            except IndexError:
                try:
                    if isinstance(f_matches[position], int):
                        result = 1
                        break
                    else:
                        result = -1
                        break
                except IndexError:
                    if isinstance(s_matches[position], int):
                        result = -1
                        break
                    else:
                        result = 1
                        break
    else:
        if not f_matches and not s_matches:
            result = 0
        elif not f_matches:
            result = -1
        elif not s_matches:
            result = 1
    if result is False:
        result = 0
    return result
