""""""
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

        expected_output = [(np.array([1, 2], dtype='int32'), np.array(['val4', 'val5', 'val6']))]
        np.testing.assert_array_equal(expected_output[0][0], faulty_lines[0][0])
        np.testing.assert_array_equal(expected_output[0][1], faulty_lines[0][1])

    def test_check_datatype_conformity_with_datatype_conformity(self):
        test_sfdb = create_test_sfdbcontainer()

        faulty_lines = sc.check_datatype_conformity(test_sfdb)

        expected_output = []
        self.assertEqual(expected_output, faulty_lines)

    def test_check_datatype_conformity_without_datatype_conformity_values_too_long(self):
        test_entries = [['12345', '56789'], ['12345', '34567']]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)

        faulty_entries = sc.check_datatype_conformity(test_sfdb)

        error_msg = 'Entry too long with 5 chars! Allowed length is 4!'
        expected_output = [(0, ' 1-COLUMN1', np.array(['12345', '56789']), '12345', error_msg),
                           (1, ' 1-COLUMN1', np.array(['12345', '34567']), '12345', error_msg),
                           (0, ' 2-COLUMN2', np.array(['12345', '56789']), '56789', error_msg),
                           (1, ' 2-COLUMN2', np.array(['12345', '34567']), '34567', error_msg)]

        for expected_entry, entry in zip(expected_output, faulty_entries):
            self.assertEqual(expected_entry[0], entry[0])
            self.assertEqual(expected_entry[0], entry[0])
            np.testing.assert_array_equal(expected_entry[2], entry[2])
            self.assertEqual(expected_entry[3], entry[3])
            self.assertEqual(expected_entry[4], entry[4])

    def test_check_datatype_conformity_without_datatype_conformity_string_for_int(self):
        test_entries = [['abcd', 'efgh'], ['ijkl', 'mnop']]
        test_schema = SQLTableSchema('INT_4_CHARACTERS')
        test_sfdb = create_test_sfdbcontainer(entries=test_entries, schema=test_schema)

        faulty_entries = sc.check_datatype_conformity(test_sfdb)

        error_msg = 'Mismatch to SQL datatype-pattern \'^\\d{1,4}$\'!'
        expected_output = [(0, ' 1-COLUMN1', np.array(['abcd', 'efgh']), 'abcd', error_msg),
                           (1, ' 1-COLUMN1', np.array(['ijkl', 'mnop']), 'ijkl', error_msg),
                           (0, ' 2-COLUMN2', np.array(['abcd', 'efgh']), 'efgh', error_msg),
                           (1, ' 2-COLUMN2', np.array(['ijkl', 'mnop']), 'mnop', error_msg)]

        for expected_entry, entry in zip(expected_output, faulty_entries):
            self.assertEqual(expected_entry[0], entry[0])
            self.assertEqual(expected_entry[0], entry[0])
            np.testing.assert_array_equal(expected_entry[2], entry[2])
            self.assertEqual(expected_entry[3], entry[3])
            self.assertEqual(expected_entry[4], entry[4])

    def test_check_content_against_regex_all_entries_match(self):
        test_sfdb = create_test_sfdbcontainer()
        test_column_patterns = {'COLUMN1': re.compile(r'val\d'),
                                'COLUMN2': re.compile(r'val\d')}

        matching_lines = sc.check_content_against_regex(test_sfdb, test_column_patterns)

        expected_output = []
        self.assertEqual(matching_lines, expected_output)

    def test_check_content_against_regex_1_value_mismatch(self):
        test_entries = [['val1', 'val2'], ['val1', '2']]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)
        test_column_patterns = {'COLUMN1': re.compile(r'val\d'),
                                'COLUMN2': re.compile(r'val\d')}

        matching_lines = sc.check_content_against_regex(test_sfdb, test_column_patterns)

        expected_entry_index = 1
        expected_column_string = " 2-COLUMN2"
        expected_entry = np.array(test_entries[1])
        expected_value = '2'
        exected_regex = r'val\d'

        self.assertEqual(expected_entry_index, matching_lines[0][0])
        self.assertEqual(expected_column_string, matching_lines[0][1])
        np.testing.assert_array_equal(expected_entry, matching_lines[0][2])
        self.assertEqual(expected_value, matching_lines[0][3])
        self.assertEqual(exected_regex, matching_lines[0][4])

    def test_check_content_against_regex_2_value_mismatch(self):
        test_entries = [['nopat1', 'nopat2'], ['val1', 'val2']]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)
        test_column_patterns = {'COLUMN1': re.compile(r'val\d'),
                                'COLUMN2': re.compile(r'val\d')}

        matching_lines = sc.check_content_against_regex(test_sfdb, test_column_patterns)

        expected_entry_index1 = 0
        expected_column_string1 = " 1-COLUMN1"
        expected_entry1 = np.array(test_entries[0])
        expected_value1 = 'nopat1'
        exected_regex1 = r'val\d'

        self.assertEqual(expected_entry_index1, matching_lines[0][0])
        self.assertEqual(expected_column_string1, matching_lines[0][1])
        np.testing.assert_array_equal(expected_entry1, matching_lines[0][2])
        self.assertEqual(expected_value1, matching_lines[0][3])
        self.assertEqual(exected_regex1, matching_lines[0][4])

        expected_entry_index2 = 0
        expected_column_string2 = " 2-COLUMN2"
        expected_entry2 = np.array(test_entries[0])
        expected_value2 = 'nopat2'
        exected_regex2 = r'val\d'

        self.assertEqual(expected_entry_index2, matching_lines[1][0])
        self.assertEqual(expected_column_string2, matching_lines[1][1])
        np.testing.assert_array_equal(expected_entry2, matching_lines[1][2])
        self.assertEqual(expected_value2, matching_lines[1][3])
        self.assertEqual(exected_regex2, matching_lines[1][4])

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

        diverging_entries = sc.check_sfdb_comparison(sfdb1, sfdb2)

        expected_output = [(1, np.array(['1', '2']),
                            1, np.array(['1', '3']))]
        self.assertEqual(expected_output[0][0], diverging_entries[0][0])
        np.testing.assert_array_equal(expected_output[0][1], diverging_entries[0][1])
        self.assertEqual(expected_output[0][2], diverging_entries[0][2])
        np.testing.assert_array_equal(expected_output[0][3], diverging_entries[0][3])

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
