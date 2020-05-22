"""This module is designed to simplify dealing with SFDBs and improve the performance of accessing and comparing SFDBs.
Each SFDB (smartFix Database) file represents a table. It has 5 header-lines that determine the tables name, the number
of columns and the name of each column. Every line that follows is an entry in the database, a line of tab-separated
values."""
import os
from functools import lru_cache

import numpy as np

from sfdbtester.sfdb.sql_table_schema import SQLTableSchema


class NotSFDBFileError(Exception):
    """This custom error is to be raised when a function/method that expects an SFDB file as parameter receives
    something else instead."""
    pass


class SFDBContainer:
    """This class is designed to contain the content of sfdb (smartFix-Datbases) files. It splits database-entries
    into numpy-arrays for faster access. Further it has an SQLTableSchemas that tells you which datatypes an SQL table,
    that you might upload this file to, would expect and enforce."""
    i_table_name_line = 2
    i_column_line = 3
    i_header_end = 5

    def __init__(self, sfdb_lines):
        self.sfdb_lines = sfdb_lines
        self.content = self.__create_sfdb_table()
        self.schema = SQLTableSchema(self.name)

    def __create_sfdb_table(self):
        """Generates a 2D numpy array of all entries in an SFDB file. Ignores the SFDB-file header."""
        content_lines = self.sfdb_lines[type(self).i_header_end:]
        return np.array([line.split('\t') for line in content_lines])

    def __len__(self):
        """Get the number of entries in the sfdb file"""
        return len(self.content)

    def __getitem__(self, key):
        """Returns content of the sfdb file based on the provided key.
        If the key is a slice object, a slice of the sfdb file is provided.
        If the key is an index, the line of the sfdb file at index is provided.
        """
        if isinstance(key, slice):  # If the key is a slice object
            start, stop, step = key.indices(len(self))
            return [self[i] for i in range(start, stop, step)]
        elif isinstance(key, int):  # If they key is an index
            if key >= len(self):
                raise IndexError(f'Index {key} is out of range of 0-{len(self)-1}')

            return self.content[key]
        else:
            raise TypeError(f'Invalid argument type for getting item from '
                            f'SFDBContainer : {type(key)}')

    def __reversed__(self):
        """Reverse the sfdb content table and return that"""
        return self.content[::-1]

    def __add__(self, other_sfdb):
        """Add 2 SFDBs with identical headers together by appending the entries of one to the other"""
        if self._is_sfdb(other_sfdb) and self.header == other_sfdb.header:
            added_content_lines = other_sfdb.sfdb_lines[type(self).i_header_end:]
            return SFDBContainer(other_sfdb.sfdb_lines + added_content_lines)
        else:
            raise ValueError('You can not add sfdb files with different headers!')

    def __radd__(self, other_sfdb):
        if other_sfdb == 0:
            return self
        else:
            return self.__add__(other_sfdb)

    def __repr__(self):
        return f'SFDBContainer of the table {self.name} with columns '\
               f'{self.columns} and {len(self.content)} entries'

    @property
    def header(self):
        """Get the lines of the table header"""
        header_lines = self.sfdb_lines[:type(self).i_header_end]
        return [line.split('\t') for line in header_lines]

    @property
    def name(self):
        """Get the name of the SQL table for this SFDB"""
        return self.header[type(self).i_table_name_line][1]

    @property
    def columns(self):
        """Get a list of the name of all columns in this sfdb file"""
        column_line = self.header[type(self).i_column_line]
        return column_line[1:]

    @classmethod
    def from_file(cls, sfdb_file_path):
        """Creates an SFDBContainer out of the contents of the passed file"""
        sfdb_lines = cls.read_sfdb_from_file(sfdb_file_path)
        return cls(sfdb_lines)

    @staticmethod
    def read_sfdb_from_file(file_path):
        """Reads in an sfdb file and turns it into a list of lists of strings.

        Parameters:
            file_path (string): Path of the sfdb file.
        Returns:
            list: List of strings. Each string is a single line in the sfdb file
            None: If file_path is empty
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'{file_path} does not exist !')

        with open(file_path, encoding="utf8") as input_stream:
            line_list = SFDBContainer._read_sfdb(input_stream)

        if not SFDBContainer._is_sfdb(line_list):
            raise NotSFDBFileError(f'{file_path} is not an SFDB! It does not have a correct sfdb header or no entries!')

        return line_list

    @staticmethod
    def _read_sfdb(sfdb_stream):
        """Reads in an sfdb file and turns it into a list of lists of strings without line-endings.

        Parameters:
            sfdb_stream (IOStream): An input output stream from which can be read.
        Returns:
            list: List of strings. Each string is a single line in the sfdb file
            None: If file_path is empty
        """
        sfdb_lines = [line.rstrip() for line in sfdb_stream.readlines()]

        if len(sfdb_lines) > 0 and sfdb_lines[-1] == '':
            del(sfdb_lines[-1])

        return sfdb_lines

    @staticmethod
    def _is_sfdb(sfdb_object):
        """Checks whether the given object represents an SFDB file. This can be either an SFDBContainer object or a list
        of strings from reading in an SFDB file. This test requires the SFDB format to be correct.

        Parameters:
            sfdb_object: Any object.
        Returns:
            boolean: True if the object does represent an SFDB, false if it does not or the SFDB is faulty.
        """
        if isinstance(sfdb_object, list):
            sfdb_line_list = sfdb_object
            has_min_length = (len(sfdb_line_list) >= 5)
            has_sfdb_header = SFDBContainer._has_sfdb_header(sfdb_line_list)
            return has_min_length and has_sfdb_header

        return isinstance(sfdb_object, SFDBContainer)

    @staticmethod
    def _has_sfdb_header(line_list):
        """Checks whether each line in the header of an sfdb file follows the sfdb format specifications."""
        if len(line_list) < 5:
            return False

        header = [line.split('\t') for line in line_list[:5]]
        is_correct_header = ((header[0][0] == 'ENCODING UTF8') and (len(header[0]) == 1) and
                             (header[1][0] == 'INIT')          and (len(header[1]) == 1) and
                             (header[2][0] == 'TABLE')         and (len(header[2]) == 2) and
                             (header[3][0] == 'COLUMNS')       and (len(header[3]) > 1) and
                             (header[4][0] == 'INSERT')        and (len(header[4]) == 1))
        return is_correct_header

    @staticmethod
    def _seq_to_sfdb_line(sfdb_sequence):
        """Turns a list or arrayinto a more easily human readable string"""
        return '\t'.join(sfdb_sequence)

    def get_entry_string(self, content_index):
        """Returns the string representation of an entry in the SFDB"""
        if not isinstance(content_index, int):
            raise TypeError(f'Index must be an integer!')
        if content_index < 0:
            raise IndexError(f'Index out of bounds. No negative Indices allowed!')

        return self.sfdb_lines[content_index + self.i_header_end]

    def has_schema(self):
        """Checks whether the sfdb file has a functional SQL Table Schema in its SQLTableSchema object"""
        return self.schema.is_full_schema()

    def write_to_file(self, filepath, remove_duplicates=False, sort=False):
        """"Creates an IOStream to a file and writes this sfdb to it. Records in written file can be sorted and have
        duplicates filtered out."""
        with open(filepath, mode='w', encoding='utf-8') as output_stream:
            self._write(output_stream, remove_duplicates=remove_duplicates, sort=sort)

    def _write(self, output_stream, remove_duplicates=False, sort=False):
        """"Writes the sfdb to an IOStream. Records in written file can be sorted and have duplicates filtered out"""
        for line in self.header:
            output_stream.write(self._seq_to_sfdb_line(line) + '\n')

        i_duplicates = self._get_duplicate_index_list()
        content = np.sort(self.content, axis=0) if sort else self.content

        for i, line in enumerate(content):
            if remove_duplicates and i in i_duplicates:
                continue
            output_stream.write(self._seq_to_sfdb_line(line) + '\n')

    def _get_duplicate_index_list(self):
        """Return a list of the indices all duplicate entries. Does not include the first occurrence of each entry."""
        duplicate_list = self.get_duplicates()
        i_duplicates = []
        for indices, line in duplicate_list:
            i_duplicates.extend(indices[1:])
        return set(i_duplicates)

    @lru_cache(3)
    def get_duplicates(self):
        """Returns a list of duplicate sfdb entries. Each entry in that list is an index list of all entries that are
        duplicates to each other. The lists are sorted smallest to largest index.
        Parameters:
            -
        Returns:
            list(array, str): The array contains all indices with the duplicate, the second is the entry itself."""
        values, inverse, count = np.unique(self.content, return_inverse=True, return_counts=True, axis=0)
        idx_values_repeated = np.where(count > 1)[0]
        if not idx_values_repeated.size > 0:
            return[]

        rows, cols = np.where(inverse == idx_values_repeated[:, np.newaxis])
        _, inverse_rows = np.unique(rows, return_index=True)

        res = np.split(cols, inverse_rows[1:])
        duplicate_list = [(i, self._seq_to_sfdb_line(self.content[i[0]])) for i in res]

        return duplicate_list
