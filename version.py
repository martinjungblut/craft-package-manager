#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import findall

# Version parsing algorithm
# 1 - Case insensitive regular expression matches letters and numbers.
# 2 - For each one of the matching groups, check whether it is possible to convert it to an integer, and do so if possible. If not possible, convert group to lowercase.
# 3 - Glue individual sequential group strings together, while keeping everything in the same order as before.
# Currently not the most efficient implementation, since it uses two lists and a buffer. In-place list manipulation would be better.
def parse(version):
    matches = findall('([aA-zZ]+|[0-9]+)', str(version))
    if matches:
        for match in matches:
            try:
                matches[matches.index(match)] = int(match)
            except:
                matches[matches.index(match)] = match.lower()
        strbuffer = ""
        new_matches = []
        for match in matches:
            if isinstance(match, str):
                strbuffer = strbuffer + match
            else:
                if strbuffer:
                    new_matches.append(strbuffer)
                    strbuffer = ""
                new_matches.append(match)
        if strbuffer:
            new_matches.append(strbuffer)
        return new_matches
    else:
        return False

# Version comparison algorithm
# 1 - Parse both versions.
# 2 - Check parsing results, and return the appropriate value in case one of the versions could not be parsed properly, or was empty.
# 3 - Compare parsing results, and in case one of them has an empty element as the current one being compared, always return -1 in case it is a string, and 1 in case it is an int.
def compare(fversion, sversion):
    fmatches = parse(fversion)
    smatches = parse(sversion)
    if not fmatches and not smatches:
        return 0
    elif not fmatches:
        return -1
    elif not smatches:
        return 1
    size = len(fmatches) if len(fmatches) > len(smatches) else len(smatches)
    for x in range(0, size):
        try:
            if fmatches[x] > smatches[x]:
                return 1
            elif fmatches[x] < smatches[x]:
                return -1
        except IndexError:
            try:
                return 1 if isinstance(fmatches[x], int) else -1
            except IndexError:
                return -1 if isinstance(smatches[x], int) else 1
    return 0
