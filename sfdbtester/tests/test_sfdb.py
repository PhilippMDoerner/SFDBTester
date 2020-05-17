import unittest as ut
from unittest import mock
import tempfile as tf
import numpy as np
from sfdbtester.sfdb.sfdb import SFDBContainer, NotSFDBFileError # FIX THIS IMPORT
from pathlib import Path


def create_test_SFDBContainer(name='Test', columns=('COLUMN1', 'COLUMN2'),
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
        self.test_sfdb = create_test_SFDBContainer()
        self.test_sfdb_filepath = get_resource_filepath('test_duplicates.sfdb')
        self.test_sfdb.write(self.test_sfdb_filepath)

        self.empty_filepath = get_resource_filepath('empty.sfdb')
        
        self.wrong_header_sfdb_filepath = get_resource_filepath('wrong_header.sfdb')

        self.tmp_filepath = get_resource_filepath('tempfile.sfdb')

    def test_header(self):
        self.assertEqual(self.test_sfdb.header[0], ['ENCODING UTF8'])
        self.assertEqual(self.test_sfdb.header[1], ['INIT'])
        self.assertEqual(self.test_sfdb.header[2], ['TABLE', 'Test'])
        self.assertEqual(self.test_sfdb.header[3], ['COLUMNS', 'COLUMN1', 'COLUMN2'])
        self.assertEqual(self.test_sfdb.header[4], ['INSERT'])

    def test_name(self):
        self.assertEqual(self.test_sfdb.name, 'Test')

        test_name2 = 'SFI_TESTTABLE2'
        test_sfdb = create_test_SFDBContainer(name=test_name2)
        self.assertNotEqual(test_sfdb.name, 'Test')

    def test_columns(self):
        self.assertEqual(self.test_sfdb.columns, ['COLUMN1', 'COLUMN2'])

        test_columns = ['C', 'D']
        test_sfdb = create_test_SFDBContainer(columns=test_columns)
        self.assertNotEqual(test_sfdb.columns, self.test_sfdb.columns)

    def test_read_sfdb_wrong_file_path(self):
        with self.assertRaises(FileNotFoundError):
            SFDBContainer.read_sfdb('/FakeDir/NotAFile.sfdb')

    def test_read_sfdb_no_permission(self):
        with mock.patch('sfdb.SFDBContainer.read_sfdb', side_effect=PermissionError, create=True):
            with self.assertRaises(PermissionError):
                SFDBContainer.read_sfdb(self.test_sfdb_filepath)

    def test_read_sfdb_empty_file(self):
        with self.assertRaises(NotSFDBFileError):
            SFDBContainer.read_sfdb(self.empty_filepath)

    def test_read_sfdb_wrong_header_sfdb(self):
        with self.assertRaises(NotSFDBFileError):
            SFDBContainer.read_sfdb(self.wrong_header_sfdb_filepath)

    def test_read_sfdb(self):
        read_sfdb_lines = SFDBContainer.read_sfdb(self.test_sfdb_filepath)
        self.assertEqual(self.test_sfdb.sfdb_lines, read_sfdb_lines)

    def test_from_file(self):
        read_sfdb = SFDBContainer.from_file(self.tmp_filepath)
        self.assertEqual(read_sfdb, self.test_sfdb)

    def test_write_invalid_filepath(self):
        with self.assertRaises(FileNotFoundError):
            self.test_sfdb.write('/FakeDir/NotAFile.sfdb')

    def test_write_no_permission(self):
        with mock.patch('sfdb.SFDBContainer.write', side_effect=PermissionError, create=True):
            with self.assertRaises(PermissionError):
                self.test_sfdb.write(self.test_sfdb_filepath)

    def test_write_without_duplicates(self):
        test_entries = [['1', '2'], ['5', '6'], ['3', '4']]
        test_sfdb = create_test_SFDBContainer(entries=test_entries)
        test_sfdb.write(self.tmp_filepath)
        expected_output = ['1\t2', '5\t6', '3\t4']

        with open(self.tmp_filepath, 'r') as f:
            read_output = f.readlines()
            read_output = [line.replace('\n', '') for line in read_output][5:]

        self.assertEqual(read_output, expected_output)

    def test_write_with_duplicates(self):
        test_entries = [['1', '2'], ['1', '2'], ['5', '6'], ['3', '4']]
        test_sfdb = create_test_SFDBContainer(entries=test_entries)
        test_sfdb.write(self.tmp_filepath)
        expected_output = ['1\t2', '5\t6', '3\t4']

        with open(self.tmp_filepath, 'r') as f:
            read_output = f.readlines()
            read_output = [line.replace('\n', '') for line in read_output][5:]

        self.assertEqual(read_output, expected_output)

    def test_write_with_duplicates_and_sorting(self):
        test_entries = [['1', '2'], ['1', '2'], ['5', '6'], ['3', '4']]
        test_sfdb = create_test_SFDBContainer(entries=test_entries)
        test_sfdb.write(self.tmp_filepath)
        expected_sorted_output = ['1\t2', '3\t4', '5\t6']
        test_sfdb.write(self.tmp_filepath, sort=True)

        with open(self.tmp_filepath, 'r') as f:
            read_output = f.readlines()
            read_output = [line.replace('\n', '') for line in read_output][5:]

        self.assertEqual(read_output, expected_sorted_output)
#########################################

    def test_get_duplicates(self):
        test_entries = [['1', '2'], ['1', '2'], ['5', '6'], ['3', '4']]
        test_sfdb = create_test_SFDBContainer(entries=test_entries)

        duplicate_list = test_sfdb.get_duplicates()
        expected_duplicates = [np.array([0, 1])]
        np.testing.assert_array_equal(duplicate_list, expected_duplicates)


if __name__ == '__main__':
    ut.main()
