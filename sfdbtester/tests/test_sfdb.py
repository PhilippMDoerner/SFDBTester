import unittest as ut
from pathlib import Path
import numpy as np
from sfdbtester.sfdb.sfdb import SFDBContainer, NotSFDBFileError


def create_test_sfdbcontainer(name='Test', columns=('COLUMN1', 'COLUMN2'),
                              entries=(('val1', 'val2'), ('val3', 'val4'))):
    """Creates an SFDBContainer object for testing"""
    columns = '\t'.join(columns)
    entries = ['\t'.join(entry) for entry in entries]
    header = ['ENCODING UTF8',
              'INIT',
              f'TABLE\t{name}',
              f'COLUMNS\t{columns}',
              f'INSERT']
    return SFDBContainer(header + entries)


def get_resource_filepath(resource_name):
    """Returns the absolute filepath of a file in the resource folder."""
    base_path = Path(__file__).parent
    file_path = (base_path / f'../resources/{resource_name}').resolve()
    return file_path


class TestSFDBContainer(ut.TestCase):
    """Class for testing the SFDBContainer class and its functions"""
    def setUp(self):
        """Sets up an sfdb and some temporary files to write to/read from."""
        pass

    def test___len__(self):
        test_sfdb = create_test_sfdbcontainer()
        num_test_sfdb_entries = 2
        self.assertEqual(num_test_sfdb_entries, len(test_sfdb))

    def test___get_item__key_is_int(self):
        test_sfdb = create_test_sfdbcontainer()
        i_test = 0

        entry1 = np.array(['val1', 'val2'])

        np.testing.assert_array_equal(entry1, test_sfdb[i_test])

    def test___get_item__key_is_int_out_of_bounds(self):
        test_sfdb = create_test_sfdbcontainer()
        i_test = 3

        with self.assertRaises(IndexError):
            entry = test_sfdb[i_test]

    def test___get_item__invalid_key(self):
        test_sfdb = create_test_sfdbcontainer()
        i_test = 'IAmAnInvalidKey'

        with self.assertRaises(TypeError):
            entry = test_sfdb[i_test]

    def test___get_item__slice(self):
        test_entries = [['1', '2'], ['3', '4'], ['5', '6']]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)

        expected_output = np.array([['1', '2']])
        np.testing.assert_array_equal(expected_output, test_sfdb[:1])

        expected_output = np.array([['1', '2'], ['3', '4']])
        np.testing.assert_array_equal(expected_output, test_sfdb[0:2])

        expected_output = np.array([['1', '2'], ['3', '4'], ['5', '6']])
        np.testing.assert_array_equal(expected_output, test_sfdb[0:])

    def test___add__(self):
        test_sfdb = create_test_sfdbcontainer()

        added_sfdb = test_sfdb + test_sfdb

        self.assertEqual(test_sfdb.header, added_sfdb.header)

        expected_output = np.array([('val1', 'val2'), ('val3', 'val4'), ('val1', 'val2'), ('val3', 'val4')])
        np.testing.assert_array_equal(expected_output, added_sfdb.content)

    def test___add__wrong_object(self):
        test_sfdb = create_test_sfdbcontainer()

        with self.assertRaises(ValueError):
            test_sfdb + 'I am an invalid partner for sfdb addition'

    def test___add__wrong_header(self):
        test_sfdb1 = create_test_sfdbcontainer()
        test_sfdb2 = create_test_sfdbcontainer(name='SFI_DIFFERENT')

        with self.assertRaises(ValueError):
            test_sfdb1 + test_sfdb2

    def test_header(self):
        test_sfdb = create_test_sfdbcontainer()

        self.assertEqual(['ENCODING UTF8'], test_sfdb.header[0])
        self.assertEqual(['INIT'], test_sfdb.header[1])
        self.assertEqual(['TABLE', 'Test'], test_sfdb.header[2])
        self.assertEqual(['COLUMNS', 'COLUMN1', 'COLUMN2'], test_sfdb.header[3])
        self.assertEqual(['INSERT'], test_sfdb.header[4])

    def test_name(self):
        test_name = 'SFI_TESTTABLE'
        test_sfdb = create_test_sfdbcontainer(name=test_name)

        self.assertEqual(test_name, test_sfdb.name)

    def test_columns(self):
        test_columns = ['C', 'D']
        test_sfdb = create_test_sfdbcontainer(columns=test_columns)

        self.assertEqual(test_columns, test_sfdb.columns)

    def test_read_sfdb_from_file_wrong_file_path(self):
        with self.assertRaises(FileNotFoundError):
            SFDBContainer.read_sfdb_from_file('/FakeDir/NotAFile.sfdb')

    def test_read_sfdb_from_file_empty_file(self):
        empty_sfdb_filepath = get_resource_filepath('empty.sfdb')

        with self.assertRaises(NotSFDBFileError):
            SFDBContainer.read_sfdb_from_file(empty_sfdb_filepath)

    def test_read_sfdb_from_file_wrong_header_sfdb(self):
        wrong_header_sfdb_filepath = get_resource_filepath('wrong_header.sfdb')

        with self.assertRaises(NotSFDBFileError):
            SFDBContainer.read_sfdb_from_file(wrong_header_sfdb_filepath)

    def test_read_sfdb_from_file_only_header(self):
        test_sfdb_filepath = get_resource_filepath('only_header.sfdb')

        read_sfdb_lines = SFDBContainer.read_sfdb_from_file(test_sfdb_filepath)

        expected_lines = ['ENCODING UTF8',
                          'INIT',
                          'TABLE	SFI_TESTTABLE',
                          'COLUMNS	COLUMN1	COLUMN2	COLUMN3',
                          'INSERT']
        self.assertEqual(expected_lines, read_sfdb_lines)

    def test_read_sfdb_from_file_single_entry(self):
        test_sfdb_filepath = get_resource_filepath('single_entry.sfdb')

        read_sfdb_lines = SFDBContainer.read_sfdb_from_file(test_sfdb_filepath)

        expected_lines = ['ENCODING UTF8',
                          'INIT',
                          'TABLE	SFI_TESTTABLE',
                          'COLUMNS	COLUMN1	COLUMN2	COLUMN3',
                          'INSERT',
                          'val1	val2	val3']
        self.assertEqual(expected_lines, read_sfdb_lines)

    def test_write_to_file_invalid_filepath(self):
        test_sfdb = create_test_sfdbcontainer()

        with self.assertRaises(FileNotFoundError):
            test_sfdb.write_to_file('FakeDir/NotValidFilepath')

    def test_write_to_file_valid_filepath(self):
        test_output_filepath = get_resource_filepath('tempfile.sfdb')
        test_sfdb = create_test_sfdbcontainer()

        test_sfdb.write_to_file(test_output_filepath)

        with open(test_output_filepath) as f:
            output = f.readlines()
        expected_output = ['ENCODING UTF8\n',
                           'INIT\n',
                           'TABLE	Test\n',
                           'COLUMNS	COLUMN1	COLUMN2\n',
                           'INSERT\n',
                           'val1	val2\n',
                           'val3	val4\n']
        self.assertEqual(expected_output, output)

    def test_write_to_file_no_duplicates(self):
        test_output_filepath = get_resource_filepath('tempfile.sfdb')
        test_sfdb = create_test_sfdbcontainer()

        test_sfdb.write_to_file(test_output_filepath)

        with open(test_output_filepath) as f:
            output = f.readlines()

        expected_output = ['ENCODING UTF8\n',
                           'INIT\n',
                           'TABLE	Test\n',
                           'COLUMNS	COLUMN1	COLUMN2\n',
                           'INSERT\n',
                           'val1	val2\n',
                           'val3	val4\n']
        self.assertEqual(expected_output, output)

    def test_write_with_duplicates(self):
        test_output_filepath = get_resource_filepath('tempfile.sfdb')
        test_entries = [['1', '2'], ['1', '2'], ['3', '4'], ['3', '4']]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)

        test_sfdb.write_to_file(test_output_filepath, remove_duplicates=True)

        with open(test_output_filepath) as f:
            output = f.readlines()
        expected_output = ['ENCODING UTF8\n',
                           'INIT\n',
                           'TABLE	Test\n',
                           'COLUMNS	COLUMN1	COLUMN2\n',
                           'INSERT\n',
                           '1	2\n',
                           '3	4\n']

        self.assertEqual(expected_output, output)

    def test_write_with_duplicates_with_sorting(self):
        test_output_filepath = get_resource_filepath('tempfile.sfdb')
        test_entries = [['3', '4'], ['3', '4'], ['1', '2'], ['1', '2']]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)

        test_sfdb.write_to_file(test_output_filepath, remove_duplicates=True, sort=True)

        with open(test_output_filepath) as f:
            output = f.readlines()
        expected_output = ['ENCODING UTF8\n',
                           'INIT\n',
                           'TABLE	Test\n',
                           'COLUMNS	COLUMN1	COLUMN2\n',
                           'INSERT\n',
                           '1	2\n',
                           '3	4\n']

        self.assertEqual(expected_output, output)

    def test_write_without_duplicates_with_sorting(self):
        test_output_filepath = get_resource_filepath('tempfile.sfdb')
        test_entries = [['5', '6'], ['3', '4'], ['1', '2']]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)

        test_sfdb.write_to_file(test_output_filepath, remove_duplicates=True, sort=True)

        with open(test_output_filepath) as f:
            output = f.readlines()
        expected_output = ['ENCODING UTF8\n',
                           'INIT\n',
                           'TABLE	Test\n',
                           'COLUMNS	COLUMN1	COLUMN2\n',
                           'INSERT\n',
                           '1	2\n',
                           '3	4\n',
                           '5	6\n']

        self.assertEqual(expected_output, output)

    def test_get_duplicates(self):
        test_entries = [('1', '2'), ('3', '4'), ('1', '2'), ('5', '6'), ('1', '2'), ('5', '6')]
        test_sfdb = create_test_sfdbcontainer(entries=test_entries)

        output = test_sfdb.get_duplicates()

        expected_output = [(np.array((0, 2, 4)), np.array(('1', '2'))),
                           (np.array((3, 5)), np.array(('5', '6')))]
        np.testing.assert_array_equal(expected_output[0][0], output[0][0])
        np.testing.assert_array_equal(expected_output[0][1], output[0][1])
        np.testing.assert_array_equal(expected_output[1][0], output[1][0])
        np.testing.assert_array_equal(expected_output[1][1], output[1][1])


if __name__ == '__main__':
    ut.main()
