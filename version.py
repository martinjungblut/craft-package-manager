#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import findall
import unittest

def parse(version):
    matches = findall('([aA-zZ]+|[0-9]+)', str(version))
    if matches:
        for match in matches:
            try:
                matches[matches.index(match)] = int(match)
            except:
                matches[matches.index(match)] = match.lower()
        return matches
    else:
        return False

def compare(fversion, sversion):
    fmatches = parse(fversion)
    smatches = parse(sversion)
    if not fmatches and not smatches:
        return 0
    elif not fmatches:
        return -1
    elif not smatches:
        return 1
    if all(isinstance(elem, str) for elem in fmatches) and all(isinstance(elem, str) for elem in smatches):
        fmatches = ''.join(fmatches)
        smatches = ''.join(smatches)
        if fmatches > smatches:
            return 1
        elif fmatches < smatches:
            return -1
        else:
            return 0
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
        self.assertEqual(parse('0.0.15-rc2.XX.3-2alPhA------TEST'), [0, 0, 15, 'rc', 2, 'xx', 3, 2, 'alpha', 'test'])
        self.assertEqual(parse('-.-.-.-'), False)
        self.assertEqual(parse(''), False)

    def test_compare(self):
        self.assertEqual(compare('', ''), 0)
        self.assertEqual(compare('0.10', '0.9'), 1)
        self.assertEqual(compare('0.10---rc2-dev.3', '0.10---rc2-dev.3'), 0)
        self.assertEqual(compare('0.100dev', '0.99'), 1)
        self.assertEqual(compare('1.1', '1.1'), 0)
        self.assertEqual(compare('1.1.3', '1.1.2'), 1)
        self.assertEqual(compare('1.111dev', '1.111-dev'), 0)
        self.assertEqual(compare('1.111dev', '1.111dev'), 0)
        self.assertEqual(compare('1.113rc2', '1.113-rc1'), 1)
        self.assertEqual(compare('1.11a', '1.11a'), 0)
        self.assertEqual(compare('1.11a', '1.9b'), 1)
        self.assertEqual(compare('1.11ba', '1.11b'), 1)
        self.assertEqual(compare('1.99', '1.99dev'), 1)
        self.assertEqual(compare('11-1-2', '9-11-2'), 1)
        self.assertEqual(compare('1111', '1111dev'), 1)
        self.assertEqual(compare('2.1', '1.1'), 1)
        self.assertEqual(compare('2.1', '2.1'), 0)
        self.assertEqual(compare('2128-1', '2128-1a'), 1)
        self.assertEqual(compare('21281', '21281a'), 1)
        self.assertEqual(compare('3.2-final', '3.2-beta'), 1)
        self.assertEqual(compare('4.1.1', '4.1.1-alpha'), 1)
        self.assertEqual(compare('B', 'b'), 0)
        self.assertEqual(compare('FINAL', 'final'), 0)
        self.assertEqual(compare('alpha', 'a'), 1)
        self.assertEqual(compare('alpha', 'a-1'), 1)
        self.assertEqual(compare('alpha', 'a-11'), 1)
        self.assertEqual(compare('alpha', 'a1'), 1)
        self.assertEqual(compare('b', 'a'), 1)
        self.assertEqual(compare('pre-alpha', 'prealpha'), 0)
        self.assertEqual(compare('pre-alpha1', 'pre-alpha1'), 0)
        self.assertEqual(compare('prealpha', 'P-R-E-A-L-P-H-A'), 0)
        self.assertEqual(compare('prealpha1', 'pre-alpha1'), 1)
        self.assertEqual(compare('rc', 'rc'), 0)
        self.assertEqual(compare('rc-----11', 'rc--11----'), 0)
        self.assertEqual(compare('rc-----11', 'rc11'), 0)
        self.assertEqual(compare('rc-----21', 'rc---'), 1)
        self.assertEqual(compare('rc-----21', 'rc11'), 1)
        self.assertEqual(compare('rc1', 'rc-1'), 0)
        self.assertEqual(compare('rc1', 'rc1'), 0)
        self.assertEqual(compare('rc21-rc22-rc23', 'rc21rc22rc23'), 0)
        self.assertEqual(compare('rc22', 'rc21-rc22-rc23'), 1)
        self.assertEqual(compare('rc3', 'rc1'), 1)

if __name__ == '__main__':
    unittest.main()
