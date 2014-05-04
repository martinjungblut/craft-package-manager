""" Provides functions for handling software version strings. """

from re import findall

def parse(version):
    """ Parses a specific software version string, and return it as a list.
    Algorithm:
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

def compare(f_version, s_version):
    """ Compares two software version strings. Works the same as C's strcmp.
    Algorithm:
    1 Parse both versions.
        * If parsing fails or any of the versions is empty, return accordingly.
    2 When the versions' length differs:
        * Treat a string remainder as lesser than no remainer.
        * Treat an integer remainer as greater than no remainder.
    3 Return 1 if f_version is greater than s_version.
    4 Return -1 if f_version is lesser than s_version.
    5 Return 0 if f_version is equal to s_version.
    """
    result = False
    f_matches = parse(f_version)
    s_matches = parse(s_version)
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
