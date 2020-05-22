import unittest as ut
import argparse
import re
from sfdbtester.common import argparser as ap
from sfdbtester.common.utilities import get_resource_filepath


class TestArgParser(ut.TestCase):
    def test_exclusion_index_too_low_index(self):
        test_index = 5
        with self.assertRaises(argparse.ArgumentTypeError):
            ap.exclusion_index(test_index)

    def test_exclusion_index_valid_index(self):
        test_index = 6
        index = ap.exclusion_index(test_index)
        self.assertEqual(test_index, index)

    def test_exclusion_index_negative_index(self):
        test_index = -1
        with self.assertRaises(argparse.ArgumentTypeError):
            ap.exclusion_index(test_index)

    def test_filepath_directory(self):
        test_filepath = get_resource_filepath('test_dir')
        with self.assertRaises(argparse.ArgumentTypeError):
            ap.filepath(test_filepath)

    def test_filepath_invalid_filepath(self):
        test_filepath = 'InvalidFilePathstring'
        with self.assertRaises(argparse.ArgumentTypeError):
            ap.filepath(test_filepath)

    def test_filepath_valid_filepath(self):
        test_filepath = get_resource_filepath('empty.sfdb')
        filepath = ap.filepath(test_filepath)
        self.assertEqual(test_filepath, filepath)

    def test_regex_invalid_regex(self):
        test_regex = r'\l\d'
        with self.assertRaises(argparse.ArgumentTypeError):
            ap.regex(test_regex)

    def test_regex_int(self):
        test_regex = 5
        with self.assertRaises(TypeError):
            ap.regex(test_regex)

    def test_regex_valid_regex(self):
        test_regex = r'\d\d'
        test_pattern = re.compile(test_regex, re.IGNORECASE)
        pattern = ap.regex(test_regex)
        self.assertEqual(test_pattern, pattern)


if __name__ == '__main__':
    ut.main()
