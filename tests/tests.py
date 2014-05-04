#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import remove
from shutil import rmtree

import sys, os, unittest
sys.path.append(os.path.abspath('../lib'))

import craft

class Version_Tests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(craft.version.parse(''), False)
        self.assertEqual(craft.version.parse('-.-.-.-'), False)
        self.assertEqual(craft.version.parse('0.127a.15-rc2.XX.3-2alPhA------TEST'), [0, 127, 'a', 15, 'rc', 2, 'xx', 3, 2, 'alphatest'])
        self.assertEqual(craft.version.parse('P-Y-T-H-O-N2,7,6'), ['python', 2, 7, 6])
        self.assertEqual(craft.version.parse('P-Y-T-H-O-N2,7,6dev'), ['python', 2, 7, 6, 'dev'])
        self.assertEqual(craft.version.parse('p-y-t-h-o-n'), ['python'])
        self.assertEqual(craft.version.parse('p-y-t-h-o-n2,7,6'), ['python', 2, 7, 6])
        self.assertEqual(craft.version.parse('p-y-t-h-o-n2.7.6'), ['python', 2, 7, 6])
        self.assertEqual(craft.version.parse('py-th-on2.7.6dev'), ['python', 2, 7, 6, 'dev'])

    # Use the expected integer as the first parameter, for legibility.
    def test_compare(self):
        self.assertEqual(-1, craft.version.compare('3.2rc0', '3.2-rc1'))
        self.assertEqual(0, craft.version.compare('',''))
        self.assertEqual(0, craft.version.compare('1.0', '1.0'))
        self.assertEqual(0, craft.version.compare('1.0-A', '1.0a'))
        self.assertEqual(0, craft.version.compare('1.0-a', '1.0a'))
        self.assertEqual(0, craft.version.compare('1.0a', '1.0a'))
        self.assertEqual(0, craft.version.compare('pre-alpha', 'prealpha'))
        self.assertEqual(0, craft.version.compare('pre-alpha-1', 'prealpha1'))
        self.assertEqual(1, craft.version.compare('1.0', '1'))
        self.assertEqual(1, craft.version.compare('1.0-aa', '1.0a'))
        self.assertEqual(1, craft.version.compare('1.0-ab', '1.0a'))
        self.assertEqual(1, craft.version.compare('1.0.1', '1.0'))
        self.assertEqual(1, craft.version.compare('1.0.1', '1.0.1dev'))
        self.assertEqual(1, craft.version.compare('1.0aa', '1.0a'))
        self.assertEqual(1, craft.version.compare('3.2', '3.2-rc1'))
        self.assertEqual(1, craft.version.compare('3.2-9999', '3.2-9998'))
        self.assertEqual(1, craft.version.compare('3.2-final', '3.2beta'))
        self.assertEqual(1, craft.version.compare('3.2final', '3.2beta'))

class Archive_GetFilesTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(craft.archive.getfiles('test.tar.gz'), ['./foo'])
        self.assertEqual(craft.archive.getfiles('invalid.tar.gz'), False)

class Archive_ExtractTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(craft.archive.extract('test.tar.gz'), True)
        self.assertEqual(craft.archive.extract('invalid.tar.gz'), False)

    def tearDown(self):
        rmtree('.craft')
        remove('foo')

if __name__ == '__main__':
    unittest.main()
