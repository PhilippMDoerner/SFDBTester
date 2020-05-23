import unittest as ut
import re
from sfdbtester.common import argparser as ap
from sfdbtester.sfdb import sfdb
from sfdbtester.common.utilities import get_resource_filepath


class TestArgParser(ut.TestCase):
    def setUp(self):
        self.test_sfdb_filepath = get_resource_filepath('test_duplicates.sfdb')

    def test_parse_args_sfdb_filepath_valid(self):
        test_args = [self.test_sfdb_filepath]

        args = ap.parse_args(test_args)

        self.assertTrue(isinstance(args.SFDBFile, sfdb.SFDBContainer))

    def test_parse_args_sfdb_filepath_empty(self):
        test_args = ['']

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = 'argument SFDBFile or -c/--comparison_sfdb: expected one argument'
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_sfdb_filepath_invalid(self):
        test_filepath = f'{get_resource_filepath("test_duplicates.sfdb")}_ThisMakesFilePathInvalid'
        test_args = [test_filepath]

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = f'The file \'{test_filepath}\' does not exist!'
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_sfdb_filepath_is_directory(self):
        test_filepath = get_resource_filepath("test_dir")
        test_args = [test_filepath]

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = f'\'{test_filepath}\' is a directory!'
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_regex_valid(self):
        test_regex = r'\d\d'
        test_args = [self.test_sfdb_filepath, '-re', test_regex]

        args = ap.parse_args(test_args)

        self.assertEqual(args.regular_expression, re.compile(test_regex, re.IGNORECASE))

    def test_parse_args_regex_invalid(self):
        test_regex = r'\l\d'
        test_args = [self.test_sfdb_filepath, '-re', test_regex]

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = f"\'{test_regex}\' is not a valid regular expression!"
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_regex_empty(self):
        test_regex = ''
        test_args = [self.test_sfdb_filepath, '-re', test_regex]

        args = ap.parse_args(test_args)

        self.assertEqual(args.regular_expression, re.compile(test_regex, re.IGNORECASE))

    def test_parse_args_valid_comparison_sfdb_filepath(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb]

        args = ap.parse_args(test_args)

        self.assertTrue(isinstance(args.SFDBFile, sfdb.SFDBContainer))

    def test_parse_args_empty_comparison_sfdb_filepath(self):
        comp_sfdb = ''
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb]

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = 'argument SFDBFile or -c/--comparison_sfdb: expected one argument'
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_invalid_comparison_sfdb_filepath(self):
        comp_sfdb = f'{get_resource_filepath("test_duplicates.sfdb")}_ThisMakesFilePathInvalid'
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb]

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = f'The file \'{comp_sfdb}\' does not exist!'
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_comparison_sfdb_filepath_is_directory(self):
        comp_sfdb = get_resource_filepath("test_dir")
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb]

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = f'\'{comp_sfdb}\' is a directory!'
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_exclusion_lines1_valid(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_exclusion_lines = ['6', '7', '8']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-x1']
        test_args.extend(test_exclusion_lines)

        args = ap.parse_args(test_args)

        expected_exclusion_lines = [6, 7, 8]
        self.assertEqual(expected_exclusion_lines, args.ex_lines1)

    def test_parse_args_exclusion_lines1_negative_indices(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_exclusion_lines = ['-6', '7', '8']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-x1']
        test_args.extend(test_exclusion_lines)

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = "The index -6 is invalid ! Negative Indices are not allowed!"
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_exclusion_lines1_header_indices(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_exclusion_lines = ['4', '7', '8']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-x1']
        test_args.extend(test_exclusion_lines)

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = f"The index 4 is invalid ! Index must be larger than 5"
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_exclusion_lines1_strings(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_exclusion_lines = ['6', 'NotAnIndex', '8']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-x1']
        test_args.extend(test_exclusion_lines)

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = f'\'NotAnIndex\' is not a number!'
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_exclusion_lines1_empty(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_exclusion_lines = ['']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-x1']
        test_args.extend(test_exclusion_lines)

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = 'argument -x1/ex_lines1 or -x2/ex_lines2: ' \
                                         'expected an argument, not an empty string'
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_exclusion_lines1_out_of_bounds(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        definitely_out_of_bounds = '15'
        test_exclusion_lines = [definitely_out_of_bounds]
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-x1']
        test_args.extend(test_exclusion_lines)

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = f'Indices {[15]} are out of bounds for'
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_exclusion_lines2_valid(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_exclusion_lines = ['6', '7', '8']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-x2']
        test_args.extend(test_exclusion_lines)

        args = ap.parse_args(test_args)

        expected_exclusion_lines = [6, 7, 8]
        self.assertEqual(expected_exclusion_lines, args.ex_lines2)

    def test_parse_args_exclusion_lines2_negative_indices(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_exclusion_lines = ['-6', '7', '8']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-x2']
        test_args.extend(test_exclusion_lines)

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = "The index -6 is invalid ! Negative Indices are not allowed!"
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_exclusion_lines2_header_indices(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_exclusion_lines = ['4', '7', '8']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-x2']
        test_args.extend(test_exclusion_lines)

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = f"The index 4 is invalid ! Index must be larger than 5"
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_exclusion_lines2_strings(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_exclusion_lines = ['6', 'NotAnIndex', '8']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-x2']
        test_args.extend(test_exclusion_lines)

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = f'\'NotAnIndex\' is not a number!'
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_exclusion_lines2_empty(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_exclusion_lines = ['']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-x2']
        test_args.extend(test_exclusion_lines)

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        error_message = str(cm.exception)
        expected_partial_error_message = 'argument -x1/ex_lines1 or -x2/ex_lines2: ' \
                                         'expected an argument, not an empty string'
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_excluded_columns_1_column(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_excluded_columns = ['COLUMN1']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-xc']
        test_args.extend(test_excluded_columns)

        args = ap.parse_args(test_args)

        expected_output = test_excluded_columns
        self.assertEqual(expected_output, args.ex_col)

    def test_parse_args_excluded_columns_2_columns(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_excluded_columns = ['COLUMN1', 'COLUMN2']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-xc']
        test_args.extend(test_excluded_columns)

        args = ap.parse_args(test_args)

        expected_output = test_excluded_columns
        self.assertEqual(expected_output, args.ex_col)

    def test_parse_args_excluded_columns_invalid_columns(self):
        comp_sfdb = get_resource_filepath('test_duplicates.sfdb')
        test_excluded_columns = ['COLUMN1', 'NonExistantColumn']
        test_args = [self.test_sfdb_filepath, '-c', comp_sfdb, '-xc']
        test_args.extend(test_excluded_columns)

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        expected_partial_error_message = f"argument -xc/-ex_col: Table columns ['NonExistantColumn'] are not present"
        error_message = str(cm.exception)
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_excluded_columns_no_comp_sfdb(self):
        test_excluded_columns = ['COLUMN1']
        test_args = [self.test_sfdb_filepath, '-xc']
        test_args.extend(test_excluded_columns)

        with self.assertRaises(ap.WrongArgumentError) as cm:
            ap.parse_args(test_args)

        expected_partial_error_message = 'argument -xc/-ex_col: Can not use argument -xc without argument -c'
        error_message = str(cm.exception)
        self.assertIn(expected_partial_error_message, error_message)

    def test_parse_args_write_on(self):
        test_filepath = get_resource_filepath('test_duplicates.sfdb')
        test_args = [test_filepath, '-w']

        args = ap.parse_args(test_args)

        self.assertTrue(args.write)

    def test_parse_args_write_off(self):
        test_filepath = get_resource_filepath('test_duplicates.sfdb')
        test_args = [test_filepath]

        args = ap.parse_args(test_args)

        self.assertFalse(args.write)

    def test_parse_args_sorted_write_on(self):
        test_filepath = get_resource_filepath('test_duplicates.sfdb')
        test_args = [test_filepath, '-w', '-s']

        args = ap.parse_args(test_args)

        self.assertTrue(args.write)
        self.assertTrue(args.sorted)

    def test_parse_args_request_mode_on(self):
        test_filepath = get_resource_filepath('test_duplicates.sfdb')
        test_args = [test_filepath, '-r']

        args = ap.parse_args(test_args)

        self.assertTrue(args.request)

    def test_parse_args_request_mode_off(self):
        test_filepath = get_resource_filepath('test_duplicates.sfdb')
        test_args = [test_filepath]

        args = ap.parse_args(test_args)

        self.assertFalse(args.request)

    def test_parse_args_sorted_write_off(self):
        test_filepath = get_resource_filepath('test_duplicates.sfdb')
        test_args = [test_filepath, '-w']

        args = ap.parse_args(test_args)

        self.assertTrue(args.write)
        self.assertFalse(args.sorted)


if __name__ == '__main__':
    ut.main()
