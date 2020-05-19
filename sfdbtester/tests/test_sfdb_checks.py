"""Test all functions within module sfdb_tests"""
import re
import unittest as ut

import numpy as np

from sfdbtester.common.utilities import get_resource_filepath
from sfdbtester.sfdb import sfdb
from sfdbtester.sfdb import sfdb_checks as sc
from sfdbtester.tests.test_sfdb import create_test_sfdbcontainer


class TestSFDBTests(ut.TestCase):
    def setUp(self):
        pass

    def test_check_content_format_wrong_content(self):
        wrong_content_format_filepath = get_resource_filepath('wrong_content_format.sfdb')
        test_sfdb = sfdb.SFDBContainer.from_file(wrong_content_format_filepath)

        faulty_lines = sc.check_content_format(test_sfdb)

        expected_output = [(6, ['val1', 'val2']),
                           (7, ['val1']),
                           (8, ['val1', 'val2', 'val3', 'val4']),
                           (9, ['val1', 'val2    val3'])]
        self.assertEqual(expected_output, faulty_lines)

    def test_check_content_format_correct_content(self):
        test_sfdb = create_test_sfdbcontainer()

        faulty_lines = sc.check_content_format(test_sfdb)

        expected_output = []
        self.assertEqual(expected_output, faulty_lines)

    def test_check_excel_autoformatting_no_autoformatting(self):
        test_sfdb = create_test_sfdbcontainer()

        faulty_lines = sc.check_excel_autoformatting(test_sfdb)

        expected_output = []
        self.assertEqual(expected_output, faulty_lines)

    def test_check_excel_autoformatting_excel_formatted_sfdb(self):
        excel_formatted_sfdb_filepath = get_resource_filepath('excel_formatting.sfdb')
        test_sfdb = sfdb.SFDBContainer.from_file(excel_formatted_sfdb_filepath)

        faulty_lines = sc.check_excel_autoformatting(test_sfdb)

        expected_output1 = (5, 0, np.array(['4.3E+04', 'val2'], dtype='<U8'))
        self.assertEqual(expected_output1[0], faulty_lines[0][0])
        self.assertEqual(expected_output1[1], faulty_lines[0][1])
        np.testing.assert_array_equal(faulty_lines[0][2], expected_output1[2])

        expected_output2 = (6, 1, np.array(['val1', '1.23E+08'], dtype='<U8'))
        self.assertEqual(expected_output2[0], faulty_lines[1][0])
        self.assertEqual(expected_output2[1], faulty_lines[1][1])
        np.testing.assert_array_equal(faulty_lines[1][2], expected_output2[2])

    def test_check_for_duplicates_no_duplicates(self):
        test_sfdb = create_test_sfdbcontainer()

        faulty_lines = sc.check_for_duplicates(test_sfdb)

        expected_output = []
        self.assertEqual(expected_output, faulty_lines)

    def test_check_for_duplicates_with_duplicates(self):
        no_duplicates_sfdb_filepath = get_resource_filepath('test_duplicates.sfdb')
        test_sfdb = sfdb.SFDBContainer.from_file(no_duplicates_sfdb_filepath)

        faulty_lines = sc.check_for_duplicates(test_sfdb)

        expected_output = [(np.array([6,7], dtype='int32'), 'val4\tval5\tval6')]
        np.testing.assert_array_equal(expected_output[0][0], faulty_lines[0][0])
        self.assertEqual(expected_output[0][1], faulty_lines[0][1])

    def test_check_datatype_conformity_with_datatype_conformity(self):
        test_sfdb = create_test_sfdbcontainer()

        faulty_lines = sc.check_datatype_conformity(test_sfdb)

        expected_output = []
        self.assertEqual(expected_output, faulty_lines)

    def test_check_datatype_conformity_without_datatype_conformity_values_too_long(self):
        test_entries = [['12345', '123456'], ['12345', '12345']]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)

        faulty_lines = sc.check_datatype_conformity(test_sfdb)

        expected_output = [(5, 0, '12345\t123456', False, True, 4),
                           (6, 0, '12345\t12345', False, True, 4),
                           (5, 1, '12345\t123456', False, True, 4),
                           (6, 1, '12345\t12345', False, True, 4)]
        self.assertEqual(expected_output, faulty_lines)

    #def test_check_datatype_conformity_without_datatype_conformity_invalid_datatype(self): # %TODO: Finish this test


    def test_check_content_against_regex_all_lines_match(self):
        test_sfdb = create_test_sfdbcontainer()
        test_pattern = re.compile('val\d\tval\d')

        matching_lines = sc.check_content_against_regex(test_sfdb, test_pattern)

        expected_output = []
        self.assertEqual(matching_lines, expected_output)

    def test_check_content_against_regex_one_line_mismatch(self):
        test_entries = [['val1', 'val2'], ['1', '2']]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)
        test_pattern = re.compile('val\d\tval\d')

        matching_lines = sc.check_content_against_regex(test_sfdb, test_pattern)

        expected_output = [(6, '1\t2')]
        self.assertEqual(expected_output, matching_lines)

    def test_check_content_against_regex_all_lines_mismatch(self):
        test_entries = [['nopat1', 'nopat2'], ['1', '2']]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)
        test_pattern = re.compile('val\d\tval\d')

        matching_lines = sc.check_content_against_regex(test_sfdb, test_pattern)

        expected_output = [(5, 'nopat1\tnopat2'),
                           (6, '1\t2')]
        self.assertEqual(expected_output, matching_lines)

    #def test_compare_sfdb_files(self): # TODO: Write these tests


    #def test_check_sfdb_comparison(self):

if __name__ == '__main__':
    ut.main()