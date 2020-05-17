"""Test all functions within module sfdb_tests"""
import unittest as ut
from sfdbtester.tests.test_sfdb import create_test_SFDBContainer
from sfdbtester.sfdb.sfdb_tests import test_sfdb_format
from unittest.mock import patch


class TestSFDBTests(ut.TestCase):
    def setUp(self):
        self.test_sfdb = create_test_SFDBContainer()

    def test_test_sfdb_format_correct_sfdb(self):
        warning_counter = test_sfdb_format(self.test_sfdb)
        self.assertEqual(warning_counter, 0)

    def test_test_sfdb_format_wrong_header(self):
        test_sfdb = create_test_SFDBContainer(name='')
        warning_counter = test_sfdb_format(test_sfdb)
        self.assertEqual(warning_counter, 1)

        test_sfdb = create_test_SFDBContainer()
        warning_counter = test_sfdb_format(test_sfdb)
        test_sfdb.sfdb_lines[0] = 'A wrong string'
        self.assertEqual(warning_counter, 1)

        test_sfdb = create_test_SFDBContainer()
        warning_counter = test_sfdb_format(test_sfdb)
        test_sfdb.sfdb_lines[1] = 'A wrong string'
        self.assertEqual(warning_counter, 1)

        test_sfdb = create_test_SFDBContainer()
        warning_counter = test_sfdb_format(test_sfdb)
        test_sfdb.sfdb_lines[2] = 'A wrong string'
        self.assertEqual(warning_counter, 1)

        test_sfdb = create_test_SFDBContainer()
        warning_counter = test_sfdb_format(test_sfdb)
        test_sfdb.sfdb_lines[3] = 'A wrong string'
        self.assertEqual(warning_counter, 1)

        test_sfdb = create_test_SFDBContainer()
        warning_counter = test_sfdb_format(test_sfdb)
        test_sfdb.sfdb_lines[4] = 'A wrong string'
        self.assertEqual(warning_counter, 1)

        test_sfdb = create_test_SFDBContainer()
        warning_counter = test_sfdb_format(test_sfdb)
        test_sfdb.sfdb_lines[0] = 'A wrong string'
        test_sfdb.sfdb_lines[1] = 'A wrong string'
        test_sfdb.sfdb_lines[2] = 'A wrong string'
        test_sfdb.sfdb_lines[3] = 'A wrong string'
        test_sfdb.sfdb_lines[4] = 'A wrong string'
        self.assertEqual(warning_counter, 1)

    def test_test_sfdb_format_wrong_content_format(self):
        test_entries = [['1', '2', '3']]
        test_columns = ['A', 'B']
        test_sfdb = create_test_SFDBContainer(entries=test_entries, columns=test_columns)
        warning_counter = test_sfdb_format(test_sfdb)
        self.assertEqual(warning_counter, 1)

    def test_test_sfdb_format_excel_formatted_entries(self):
        test_entries = [['1E+09', '2']]
        test_sfdb = create_test_SFDBContainer(entries=test_entries)
        warning_counter = test_sfdb_format(test_sfdb)
        self.assertEqual(warning_counter, 1)

    def test_test_sfdb_format_duplicate_entries(self):
        test_entries = [['1', '2'], ['1', '2'], ['3', '4'], ['3', '4']]
        test_sfdb = create_test_SFDBContainer(entries=test_entries)
        warning_counter = test_sfdb_format(test_sfdb)
        self.assertEqual(warning_counter, 2)

#def test_sfdb_for_similars(sfdb, max_differences, similarity_threshold):
#def test_sfdb_against_regex(sfdb, regex_pattern):
#def test_sfdb_datatypes(sfdb):
#def check_datatype_conformity(sfdb):
#def compare_sfdb_files(sfdb_new, sfdb_old, excluded_entries_new, excluded_entries_old, excluded_columns):
#def _list_to_string(aList):
#def _compare_sfdb_entries(sfdb_new, sfdb_old,
#def _compare_entries(new_entry, old_entry, i_ex_col_new, i_ex_col_old):
#def check_header_format(sfdb):
#def check_content_format(sfdb):
#def check_excel_autoformatting(sfdb):
#def check_for_duplicates(sfdb):
#def check_content_against_regex(sfdb, regex_string):
