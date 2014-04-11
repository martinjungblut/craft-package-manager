#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import findall
import unittest

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

class Tests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse(''), False)
        self.assertEqual(parse('-.-.-.-'), False)
        self.assertEqual(parse('0.127a.15-rc2.XX.3-2alPhA------TEST'), [0, 127, 'a', 15, 'rc', 2, 'xx', 3, 2, 'alphatest'])
        self.assertEqual(parse('P-Y-T-H-O-N2,7,6'), ['python', 2, 7, 6])
        self.assertEqual(parse('P-Y-T-H-O-N2,7,6dev'), ['python', 2, 7, 6, 'dev'])
        self.assertEqual(parse('p-y-t-h-o-n'), ['python'])
        self.assertEqual(parse('p-y-t-h-o-n2,7,6'), ['python', 2, 7, 6])
        self.assertEqual(parse('p-y-t-h-o-n2.7.6'), ['python', 2, 7, 6])
        self.assertEqual(parse('py-th-on2.7.6dev'), ['python', 2, 7, 6, 'dev'])

    # Use the expected integer as the first parameter, for legibility.
    def test_compare(self):
        self.assertEqual(-1, compare('3.2rc0', '3.2-rc1'))
        self.assertEqual(0, compare('',''))
        self.assertEqual(0, compare('1.0', '1.0'))
        self.assertEqual(0, compare('1.0-A', '1.0a'))
        self.assertEqual(0, compare('1.0-a', '1.0a'))
        self.assertEqual(0, compare('1.0a', '1.0a'))
        self.assertEqual(0, compare('pre-alpha', 'prealpha'))
        self.assertEqual(0, compare('pre-alpha-1', 'prealpha1'))
        self.assertEqual(1, compare('1.0', '1'))
        self.assertEqual(1, compare('1.0-aa', '1.0a'))
        self.assertEqual(1, compare('1.0-ab', '1.0a'))
        self.assertEqual(1, compare('1.0.1', '1.0'))
        self.assertEqual(1, compare('1.0.1', '1.0.1dev'))
        self.assertEqual(1, compare('1.0aa', '1.0a'))
        self.assertEqual(1, compare('3.2', '3.2-rc1'))
        self.assertEqual(1, compare('3.2-9999', '3.2-9998'))
        self.assertEqual(1, compare('3.2-final', '3.2beta'))
        self.assertEqual(1, compare('3.2final', '3.2beta'))

if __name__ == '__main__':
    unittest.main()
