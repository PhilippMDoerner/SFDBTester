import re
import unittest as ut

import numpy as np

from sfdbtester.common.utilities import get_resource_filepath
from sfdbtester.sfdb import sfdb
from sfdbtester.sfdb import sfdb_checks as sc
from sfdbtester.sfdb.sql_table_schema import SQLTableSchema
from sfdbtester.tests.test_sfdb import create_test_sfdbcontainer


class TestSFDBTests(ut.TestCase):
    def setUp(self):
        pass

    def test_check_content_format_wrong_content(self):
        wrong_content_format_filepath = get_resource_filepath('wrong_content_format.sfdb')
        test_sfdb = sfdb.SFDBContainer.from_file(wrong_content_format_filepath)

        faulty_lines = sc.check_content_format(test_sfdb)

        expected_output = [(1, ['val1', 'val2']),
                           (2, ['val1']),
                           (3, ['val1', 'val2', 'val3', 'val4']),
                           (4, ['val1', 'val2    val3'])]
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

        expected_output1 = (0, 0, np.array(['4.3E+04', 'val2'], dtype='<U8'))
        self.assertEqual(expected_output1[0], faulty_lines[0][0])
        self.assertEqual(expected_output1[1], faulty_lines[0][1])
        np.testing.assert_array_equal(faulty_lines[0][2], expected_output1[2])

        expected_output2 = (1, 1, np.array(['val1', '1.23E+08'], dtype='<U8'))
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

        expected_output = [(np.array([1, 2], dtype='int32'), 'val4\tval5\tval6')]
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

        expected_output = [(0, 0, '12345\t123456', False, True, 4),
                           (1, 0, '12345\t12345', False, True, 4),
                           (0, 1, '12345\t123456', False, True, 4),
                           (1, 1, '12345\t12345', False, True, 4)]
        self.assertEqual(expected_output, faulty_lines)

    def test_check_datatype_conformity_without_datatype_conformity_string_for_int(self):
        test_entries = [['abcd', 'efgh'], ['ijkl', 'mnop']]
        test_schema = SQLTableSchema('INT_4_CHARACTERS')
        test_sfdb = create_test_sfdbcontainer(entries=test_entries, schema=test_schema)

        faulty_lines = sc.check_datatype_conformity(test_sfdb)

        expected_output = [(0, 0, 'abcd\tefgh', False, True, 4),
                           (1, 0, 'ijkl\tmnop', False, True, 4),
                           (0, 1, 'abcd\tefgh', False, True, 4),
                           (1, 1, 'ijkl\tmnop', False, True, 4)]
        self.assertEqual(expected_output, faulty_lines)

    def test_check_content_against_regex_all_lines_match(self):
        test_sfdb = create_test_sfdbcontainer()
        test_pattern = re.compile(r'val\d\tval\d')

        matching_lines = sc.check_content_against_regex(test_sfdb, test_pattern)

        expected_output = []
        self.assertEqual(matching_lines, expected_output)

    def test_check_content_against_regex_one_line_mismatch(self):
        test_entries = [['val1', 'val2'], ['1', '2']]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)
        test_pattern = re.compile(r'val\d\tval\d')

        matching_lines = sc.check_content_against_regex(test_sfdb, test_pattern)

        expected_output = [(1, '1\t2')]
        self.assertEqual(expected_output, matching_lines)

    def test_check_content_against_regex_all_lines_mismatch(self):
        test_entries = [['nopat1', 'nopat2'], ['1', '2']]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)
        test_pattern = re.compile(r'val\d\tval\d')

        matching_lines = sc.check_content_against_regex(test_sfdb, test_pattern)

        expected_output = [(0, 'nopat1\tnopat2'),
                           (1, '1\t2')]
        self.assertEqual(expected_output, matching_lines)

    def test_check_sfdb_comparison_identical_sfdb(self):
        sfdb1 = create_test_sfdbcontainer()
        sfdb2 = create_test_sfdbcontainer()

        diverging_lines = sc.check_sfdb_comparison(sfdb1, sfdb2)

        expected_output = []
        self.assertEqual(expected_output, diverging_lines)

    def test_check_sfdb_comparison_identical_sfdb_1_line_difference(self):
        entries1 = [['1', '2'], ['1', '2']]
        entries2 = [['1', '2'], ['1', '3']]
        sfdb1 = create_test_sfdbcontainer(entries=entries1)
        sfdb2 = create_test_sfdbcontainer(entries=entries2)

        diverging_lines = sc.check_sfdb_comparison(sfdb1, sfdb2)

        expected_output = [(1, '1\t2', 1, '1\t3')]
        self.assertEqual(expected_output, diverging_lines)

    def test_check_sfdb_comparison_identical_sfdb_1_line_difference_excluded(self):
        entries1 = [['1', '2'], ['1', '2']]
        entries2 = [['1', '2'], ['1', '3']]
        sfdb1 = create_test_sfdbcontainer(entries=entries1)
        sfdb2 = create_test_sfdbcontainer(entries=entries2)
        excluded_lines1 = [1 + sc.INDEX_SHIFT]
        excluded_lines2 = [1 + sc.INDEX_SHIFT]

        diverging_lines = sc.check_sfdb_comparison(sfdb1, sfdb2,
                                                   excluded_lines_new=excluded_lines1,
                                                   excluded_lines_old=excluded_lines2)

        expected_output = []
        self.assertEqual(expected_output, diverging_lines)

    def test_check_sfdb_comparison_sfdb_old_longer(self):
        entries1 = [['1', '2'], ['1', '2']]
        entries2 = [['1', '2'], ['1', '2'], ['1', '3']]
        sfdb1 = create_test_sfdbcontainer(entries=entries1)
        sfdb2 = create_test_sfdbcontainer(entries=entries2)

        with self.assertRaises(sc.ComparisonError):
            sc.check_sfdb_comparison(sfdb1, sfdb2)

    def test_check_sfdb_comparison_sfdb_new_longer(self):
        entries1 = [['1', '2'], ['1', '2'], ['1', '3']]
        entries2 = [['1', '2'], ['1', '2']]
        sfdb1 = create_test_sfdbcontainer(entries=entries1)
        sfdb2 = create_test_sfdbcontainer(entries=entries2)

        with self.assertRaises(sc.ComparisonError):
            sc.check_sfdb_comparison(sfdb1, sfdb2)

    def test_check_sfdb_comparison_sfdb_new_longer_insufficient_excluded_lines(self):
        entries1 = [['1', '2'], ['1', '2'], ['1', '3'], ['1', '4']]
        entries2 = [['1', '2'], ['1', '2']]
        sfdb1 = create_test_sfdbcontainer(entries=entries1)
        sfdb2 = create_test_sfdbcontainer(entries=entries2)
        excluded_lines1 = [2 + sc.INDEX_SHIFT]

        with self.assertRaises(sc.ComparisonError):
            sc.check_sfdb_comparison(sfdb1, sfdb2, excluded_lines_new=excluded_lines1)

    def test_check_sfdb_comparison_sfdb_old_longer_insufficient_excluded_lines(self):
        entries1 = [['1', '2'], ['1', '2']]
        entries2 = [['1', '2'], ['1', '2'], ['1', '3'], ['1', '4']]
        sfdb1 = create_test_sfdbcontainer(entries=entries1)
        sfdb2 = create_test_sfdbcontainer(entries=entries2)
        excluded_lines2 = [2 + sc.INDEX_SHIFT]

        with self.assertRaises(sc.ComparisonError):
            sc.check_sfdb_comparison(sfdb1, sfdb2, excluded_lines_old=excluded_lines2)

    def test_check_sfdb_comparison_sfdb_old_longer_sufficient_excluded_lines(self):
        entries1 = [['1', '2'], ['1', '2']]
        entries2 = [['1', '2'], ['1', '2'], ['1', '3'], ['1', '4']]
        sfdb1 = create_test_sfdbcontainer(entries=entries1)
        sfdb2 = create_test_sfdbcontainer(entries=entries2)
        excluded_lines2 = [2 + sc.INDEX_SHIFT,
                           3 + sc.INDEX_SHIFT]

        diverging_lines = sc.check_sfdb_comparison(sfdb1, sfdb2, excluded_lines_old=excluded_lines2)

        expected_output = []
        self.assertEqual(expected_output, diverging_lines)

    def test_check_sfdb_comparison_sfdb_new_longer_sufficient_excluded_lines(self):
        entries1 = [['1', '2'], ['1', '2'], ['1', '3'], ['1', '4']]
        entries2 = [['1', '2'], ['1', '2']]
        sfdb1 = create_test_sfdbcontainer(entries=entries1)
        sfdb2 = create_test_sfdbcontainer(entries=entries2)
        excluded_lines1 = [2 + sc.INDEX_SHIFT,
                           3 + sc.INDEX_SHIFT]

        diverging_lines = sc.check_sfdb_comparison(sfdb1, sfdb2, excluded_lines_new=excluded_lines1)

        expected_output = []
        self.assertEqual(expected_output, diverging_lines)

    def test_check_sfdb_comparison_1_column_difference_excluded(self):
        columns = ['COLUMN1', 'COLUMN2']
        entries1 = [['1', '2'], ['1', '2']]
        entries2 = [['1', '2'], ['1', '3']]
        sfdb1 = create_test_sfdbcontainer(entries=entries1, columns=columns)
        sfdb2 = create_test_sfdbcontainer(entries=entries2, columns=columns)
        excluded_columns = ['COLUMN2']

        diverging_lines = sc.check_sfdb_comparison(sfdb1, sfdb2, excluded_columns=excluded_columns)

        expected_output = []
        self.assertEqual(expected_output, diverging_lines)

    def test_check_sfdb_comparison_multiple_column_difference_excluded(self):
        columns = ['COLUMN1', 'COLUMN2', 'COLUMN3']
        entries1 = [['1', '2'], ['1', '2'], ['1', '2']]
        entries2 = [['1', '2'], ['1', '3'], ['1', '4']]
        sfdb1 = create_test_sfdbcontainer(entries=entries1, columns=columns)
        sfdb2 = create_test_sfdbcontainer(entries=entries2, columns=columns)
        excluded_columns = ['COLUMN2', 'COLUMN3']

        diverging_lines = sc.check_sfdb_comparison(sfdb1, sfdb2, excluded_columns=excluded_columns)

        expected_output = []
        self.assertEqual(expected_output, diverging_lines)


if __name__ == '__main__':
    ut.main()
