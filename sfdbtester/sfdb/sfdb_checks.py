"""This module checks SFDBContainer objects for various properties, such as whether it has duplicates, has correct
format or whether all of the values in their columns correspond to the columsn expected SQL datatype. Further it
contains log methods to write the result of the checks into a log-file."""
import logging
import re

import numpy as np

from sfdbtester.common.sfdb_logging import LOGFILE_LEVEL
from sfdbtester.sfdb.sfdb import entry_to_line

INDEX_SHIFT = 5+1  # The shift between an (machine) entry index and a (human) line index of that entry in the sfdb file

# TODO: Move all logging calls that you can that are in the "check" functions out of there into other parts of the code
# TODO: Amend all commit messages to better represent the project


class ComparisonError(Exception):
    pass


def log_sfdb_content_format_check(column_count, faulty_entries):
    """Logs the result of a check of an sfdb's content format.
    Parameters:
        column_count (int): The number of columns in the sfdb and thus the number of values each entry must have.
        faulty_entries(list(int, string)): The entries with incorrect format and their indices.
    Returns:
        Nothing
    """
    if len(faulty_entries) == 0:
        logging.log(LOGFILE_LEVEL, '    No issues.')
        return

    column1 = f'{"Line":>12}'
    column2 = '# Values'
    column3 = 'Entry'
    logging.log(LOGFILE_LEVEL, f'    Required number of values: {column_count}\n'
                               f' {column1} | {column2} | {column3}')

    for entry_index, entry in faulty_entries:
        line_index = f'{entry_index + INDEX_SHIFT:>{len(column1)}}'
        value_count = f'{len(entry):<{len(column2)}}'
        line = entry_to_line(entry)

        logging.log(LOGFILE_LEVEL, f' {line_index} | {value_count} | {line}')


def check_content_format(sfdb):
    """Checks whether each entry in the SFDB file has the correct amount
        of values aka number of cells. Each entry must have as many cells
        as there are columns specified in the header.

    Parameters:
        sfdb (SFDBContainer): The SFDB file.
    Returns:
        list: List of tuples (i(int), entry(string)) containing the index
            of an entry with wrong number of values as well as the entry itself.
    """
    num_columns = len(sfdb.columns)
    return [(i, entry) for i, entry in enumerate(sfdb.content) if not len(entry) == num_columns]


def log_excel_autoformatting_check(formatted_cells_list):
    """Logs the result of a check whether an sfdb had entries with signs of excel autoformatting.
    Parameters:
        formatted_cells_list (list(int, int, string): The entries with excel autoformatting, the entries index and the
            index of the column with the value displaying excel autoformatting.
    Returns:
        Nothing
    """
    if len(formatted_cells_list) == 0:
        logging.log(LOGFILE_LEVEL, '    No issues.')
        return

    column1 = f'{"Line":>12}'
    column2 = 'Entry'
    table_header = f' {column1} | {column2}'
    logging.log(LOGFILE_LEVEL, table_header)

    for i_entry, i_col, entry in formatted_cells_list:
        line_index = f'{i_entry + INDEX_SHIFT:>{len(column1)}}'
        line = entry_to_line(entry)
        logging.log(LOGFILE_LEVEL, f' {line_index} | \'{line}\'')


def check_excel_autoformatting(sfdb):
    """Checks whether any value in an SFDB file is a number that was
    automatically formatted by excel (e.g. 1 000 000 000) to
    scientific notation (1E+9).

    Parameters:
        sfdb (SFDBContainer): The SFDB file.
    Returns:
        list: List of tuples (i (int),j (int), entry(str)).
                i: index of an entry with a value displaying excel autoformatting
                j: index of the entry's column with the value displaying excel autoformatting
                entry : The entry with the value that displaying excel autoformatting
    """
    entries = sfdb.content
    excel_formatted_cells = []
    for i, entry in enumerate(entries):

        for j, column in enumerate(entry):
            cell_value = str(column)
            if re.search(r'\dE\+\d', cell_value) is not None:
                excel_formatted_cells.append((i, j, entry))

    return excel_formatted_cells


def log_duplicates_check(duplicates_list):
    """Logs the result of a check whether an sfdb had any duplicate entries.
    Parameters:
        duplicates_list (list(list(int), string)): A list of indices that share an identical entry as well as the
            entry itself.
    Returns:
        Nothing
    """
    if len(duplicates_list) == 0:
        logging.log(LOGFILE_LEVEL, '    No issues.')
        return

    column1 = f'{"Line":>12}'
    column2 = 'Duplicate Lines'
    column3 = 'Entry'
    logging.log(LOGFILE_LEVEL, f' {column1} | {column2} | {column3}')

    for entry_indices, entry in duplicates_list:
        line_indices = [i + INDEX_SHIFT for i in entry_indices]
        first_index = f'{line_indices[0]:>{len(column1)}}'

        duplicate_indices_string = str(line_indices[1:])[1:-1]
        other_occurrences = f'{duplicate_indices_string:<{len(column2)}}'

        line = entry_to_line(entry)

        logging.log(LOGFILE_LEVEL, f' {first_index} | {other_occurrences} | \'{line}\'')


def check_for_duplicates(sfdb):
    """Checks whether an SFDB file has duplicate entries.
    Parameters:
        sfdb (SFDBContainer): The SFDB file.
    Returns:
        list (list(int), str) : List of entry-indices with identical entries and the entry itself. 
            Entry-indices start from 0.
    """
    return sfdb.get_duplicates()


def log_regex_check(non_regex_lines, regex_pattern):
    """Logs the result of a check whether an sfdb had a valid header
    Parameters:
        non_regex_lines (list(int, string)): A list of lines that didn't match the regular expression in regex_pattern
            and their indices in the file.
        regex_pattern (Pattern): A re.Pattern object of the regular expression that was searched for.
    Returns:
        Nothing
    """
    if len(non_regex_lines) == 0:
        logging.log(LOGFILE_LEVEL, '    No issues.')
        return

    logging.log(LOGFILE_LEVEL, f'    Regex: \"{str(regex_pattern)[12:-2]}\":')

    column1 = f'{"Line":<12}'
    column2 = 'Entry'
    logging.log(LOGFILE_LEVEL, f' {column1} | {column2}')

    for i, line in non_regex_lines:
        line_index = f'{i + INDEX_SHIFT:>{len(column1)}}'
        logging.log(LOGFILE_LEVEL, f' {line_index} | \'{line}\'')


def check_content_against_regex(sfdb, regex_pattern):
    """Checks whether an SFDB file has lines without values that match a regular
    expression. Excludes the SFDB header lines from the search.

    Parameters:
        sfdb (SFDBContainer): The SFDB file.
        regex_pattern (Pattern): The regular expression.
    Returns:
        list: A list of tuples(i (int), line (list)).
                i: Index of line that did not match regular expression.
                line : List of strings. A line that did not contain the
                    regular expression
        None: If regular expression pattern object is "None".
    """

    if regex_pattern is None:
        lines_without_regex = None
    else:
        sfdb_lines = sfdb.sfdb_lines[5:]
        lines_without_regex = [(i, line) for i, line in enumerate(sfdb_lines)
                               if not regex_pattern.search(str(line))]
    return lines_without_regex


def log_datatype_check(non_conform_entries):
    """Logs the result of a check whether an sfdb had a valid header
    Parameters:
        non_conform_entries (): A list of entries where 1 or more values did not conform with their column's datatype.
    Returns:
        Nothing
    """
    if non_conform_entries is None:
        logging.log(LOGFILE_LEVEL, '    No Column Definitions found. Test skipped')
        return

    elif len(non_conform_entries) == 0:
        logging.log(LOGFILE_LEVEL, '    No issues.')
        return

    column1 = f'{"Line":>12}'
    column2 = f'{"Column_index - Column":<25}'
    column3 = f'{"Error Message":<60}'
    column4 = f'{"Faulty Value":<20}'
    column5 = 'Entry'
    logging.log(LOGFILE_LEVEL, f' {column1} | {column2} | {column3} | {column4} | {column5}')

    for entry_index, column_string, entry, faulty_value, error_msg in non_conform_entries:
        line_index = f'{entry_index + INDEX_SHIFT:>{len(column1)}}'
        column = f'{column_string:<{len(column2)}}'
        error_string = f'{error_msg:<{len(column3)}}'
        value = f'{faulty_value:<20}'
        line = entry_to_line(entry)

        logging.log(LOGFILE_LEVEL, f' {line_index} | {column} | {error_string} | {value} | \'{line}\'')


def check_datatype_conformity(sfdb):
    """Tests whether all values/cells in an SFDB file are in accordance
    with their assigned SQL datatype in the corresponding SQL table.

    Parameters:
        sfdb (SFDBContainer): The SFDB file
    Returns:
        list: A list of tuples (entry_index (int), column_string (str), entry(np.ndarray), cell_value, error_msg (str)).
            entry_index: The index of the entry that has a faulty value
            column_string: A string representation of the column that has a faulty value. Includes the column's index.
            entry: An SFDBContainer entry, thus a 1 dimensional numpy ndarray
            cell_value: The faulty cell value. Is either int or str
            error_msg: An error message explaining why the cell_value is faulty.
    """
    if not sfdb.has_schema():
        return None

    list_of_issues = []
    for column_index, column_name in enumerate(sfdb.columns):
        column = sfdb.schema[column_name]
        regex_pattern = sfdb.schema.get_datatype_regex_pattern(column_name)

        if regex_pattern is None:  # if datatype is not known to function, skip comparison
            logging.log(LOGFILE_LEVEL, f'    Skipped comparison! {column_name} has unknown datatype {column.datatype}.')
            continue

        for entry_index, entry in enumerate(sfdb.content):
            cell_value = entry[column_index]

            if _is_non_conform_with_column(cell_value, column, regex_pattern):
                column_string = f'{column_index + 1:>2}-{column.name}'
                error_msg = _get_datatype_error_message(cell_value, column, regex_pattern)

                list_of_issues.append((entry_index, column_string, entry, cell_value, error_msg))

    return list_of_issues


def _is_non_conform_with_column(entry, column, column_pattern):
    """Determines whether an entry is conform with a column's datatype or not."""
    has_illegal_null = not column.with_null and entry == ''
    entry_too_long = len(entry) > column.length
    entry_not_match = column_pattern.search(entry) is None
    return has_illegal_null or entry_too_long or entry_not_match


def _get_datatype_error_message(entry, column, column_pattern):
    """Determines the error message why this entry was not conform with the column's datatype"""
    has_illegal_null = not column.with_null and entry == ''
    entry_too_long = len(entry) > column.length
    entry_not_match = column_pattern.search(entry) is None

    if has_illegal_null:
        return "Null not allowed in column !"
    elif entry_too_long:
        return f"Entry too long with {len(entry)} chars! Allowed length is {column.length}!"
    elif entry_not_match:
        return f"Mismatch to SQL datatype-pattern \'{column_pattern.pattern}\'!"
    else:
        return "Unknown Error"


def log_sfdb_comparison(diverging_lines):
    if diverging_lines is None:
        log_message = '    Comparison Test Skipped. Files did not have equal lengths with the given lines excluded.'
        logging.log(LOGFILE_LEVEL, log_message)
        return

    elif len(diverging_lines) == 0:
        logging.log(LOGFILE_LEVEL, '    No issues.')
        return

    column1 = '   Linetype'
    column2 = f'{"Index":<8}'
    column3 = 'Entry'
    logging.log(LOGFILE_LEVEL, f' {column1} | {column2} | {column3}')

    for i_new, entry_new, i_old, entry_old in diverging_lines:
        line_index_old = f'{i_old + INDEX_SHIFT:>{len(column2)}}'
        line_new = entry_to_line(entry_new)
        line_index_new = f'{i_new + INDEX_SHIFT:>{len(column2)}}'
        line_old = entry_to_line(entry_old)

        logging.log(LOGFILE_LEVEL, f' {f"Old":>{len(column1)}} | {line_index_old} | \'{line_old}\'\n'
                                   f' {f"New":>{len(column1)}} | {line_index_new} | \'{line_new}\'\n')


def check_sfdb_comparison(sfdb_new, sfdb_old, excluded_lines_new=(), excluded_lines_old=(), excluded_columns=()):
    """Checks whether the lines of 2 SFDB files are identical after
    exclusion of added/deleted lines and columns.

    Excluded lines and columns are specified via user-input. 

    Parameters:
        sfdb_new (SFDBContainer): The updated version of an SFDB file.
        sfdb_old (SFDBContainer): The previous version of an SFDB file.
        excluded_lines_new (list): List of entry indices from sfdb_new that shall not be compared.
        excluded_lines_old (list): List of entry indices from sfdb_old that shall not be compared.
        excluded_columns (list): List of strings. The columns that shall be ignored for the comparison.
    Returns:
        int: Number of warnings raised.
    """
    logging.log(LOGFILE_LEVEL, f'    Excluded lines in Old? {excluded_lines_old}')
    logging.log(LOGFILE_LEVEL, f'    Excluded lines in New? {excluded_lines_new}')
    logging.log(LOGFILE_LEVEL, f'    Excluded columns?      {excluded_columns}')

    # Change indices from (start at 6) to (start at 0)
    excluded_entries_new = [] if excluded_lines_new is None else \
        set([line_index - INDEX_SHIFT for line_index in excluded_lines_new])

    excluded_entries_old = [] if excluded_lines_new is None else \
        set([line_index - INDEX_SHIFT for line_index in excluded_lines_old])

    if not sfdb_new.name == sfdb_old.name:
        logging.log(LOGFILE_LEVEL, '    !WARNING! SQL Tables have different names!')

    deviating_lines = _compare_sfdb_lines(sfdb_new,
                                          sfdb_old,
                                          excluded_entries_new,
                                          excluded_entries_old,
                                          excluded_columns)
    return deviating_lines


def _compare_sfdb_lines(sfdb_new, sfdb_old, i_ex_entries_new, i_ex_entries_old, excluded_columns):
    """Checks whether the lines of 2 SFDB files are identical after exclusion of specific lines and columns.

    Compares SFDB header and content separately. Raises a ComparisonError if the SFDB files don't have identical
    numbers of lines after exclusion of the specified lines. Loops over SFDB content and first checks every
    iteration whether a line in sfdb_new or sfdb_old must be skipped.

    Parameters:
        sfdb_new (SFDBContainer): The updated version of an SFDB file.
        sfdb_old (SFDBContainer): The previous version of an SFDB file.
        i_ex_entries_new (set): Set of int. Entry-indices to be excluded from sfdb_new
        i_ex_entries_old (set): Set of int. Entry-indices to be excluded from sfdb_old
        excluded_columns (list): List of strings. Names columns to be
            excluded from both sfdb files.
    Returns:
        list: List of tuples (i (int), new_entry(np.ndarray), j (int), old_entry(np.ndarray).
                i: Index of deviating line in sfdb_new
                new_entry: Numpy ndarray of strings. The entry in the sfdb_new.
                j: Index of deviating line in sfdb_old
                new_entry: Numpy ndarray of strings. The entry in the sfdb_old.
    """
    if not len(sfdb_new) - len(i_ex_entries_new) == len(sfdb_old) - len(i_ex_entries_old):
        raise ComparisonError('Can not compare SFDB files with unequal number of lines!')

    i_ex_col_new = []
    i_ex_col_old = []
    if excluded_columns is not None:
        i_ex_col_new = [sfdb_new.columns.index(col) for col in excluded_columns]
        i_ex_col_old = [sfdb_old.columns.index(col) for col in excluded_columns]

    deviating_lines = [(i - INDEX_SHIFT, sfdb_new.header[i], i - INDEX_SHIFT, sfdb_old.header[i])
                       for i in range(len(sfdb_new.header))
                       if not sfdb_new.header[i] == sfdb_old.header[i]]

    i = 0
    j = 0
    while i in range(len(sfdb_new)) and j in range(len(sfdb_old)):
        if i in i_ex_entries_new:
            i += 1
            continue

        if j in i_ex_entries_old:
            j += 1
            continue

        if not _are_equal_entries(sfdb_new[i], sfdb_old[j], i_ex_col_new, i_ex_col_old):
            deviating_lines.append((i, sfdb_new[i], j, sfdb_old[j]))
        i += 1
        j += 1

    return deviating_lines


def _are_equal_entries(entry1, entry2, excluded_indices1, excluded_indices2):
    """Checks whether 2 entries are identical or not.

    Loops over the values and compares value by value. Checks every
    iteration first whether a value in either line must be skipped.
    Raises a ComparisonError if the lines don't have identical
    numbers of value after exclusion of the specified values.

    Parameters:
        entry1(np.ndarray): Numpy ndarray of strings. An entry from an SFDB file.
        entry2(np.ndarray): Numpy ndarray of strings. An entry from an SFDB file.
        excluded_indices1(list): List of int. Indices of values in entry1 that are excluded from the comparison.
        excluded_indices2(list): List of int. Indices of values in entry2 that are excluded from the comparison.
    Returns:
        bool: True if entries are identical. False if they are not.
    """
    if not len(entry1) - len(excluded_indices1) == len(entry2) - len(excluded_indices2):
        raise ComparisonError(f'Can not compare SFDB entries with unequal number of values!\n'
                              f'# Entry 1 : {len(entry1)}\n'
                              f'# Entry 2 : {len(entry2)}\n'
                              f'Excluded Columns 1: {excluded_indices1}\n'
                              f'Excluded Columns 2: {excluded_indices2}')

    i = 0
    j = 0
    while i < len(entry1) and j < len(entry2):
        if not excluded_indices1 == [] and i in excluded_indices1:
            i += 1
            continue

        if not excluded_indices2 == [] and j in excluded_indices2:
            j += 1
            continue

        if not entry1[i] == entry2[j]:
            return False

        i += 1
        j += 1

    return True
