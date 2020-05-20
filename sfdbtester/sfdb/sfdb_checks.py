import logging
import re

import numpy as np

from sfdbtester.sfdb.sfdb import SFDBContainer

MAX_DIGITS = 10
INDEX_SHIFT = 6  # The shift between an (machine) entry index and a (human) line index of that entry in the sfdb file

# TODO: Move all logging calls that you can that are in the "check" functions out of there into other parts of the code


class ComparisonError(Exception):
    pass


def log_sfdb_content_format_check(column_count, faulty_lines):
    """Logs the result of a check of an sfdb's content format.
    Parameters:
        column_count (int): The number of columns in the sfdb and thus the number of values each entry must have.
        faulty_lines(list(int, string)): The lines with incorrect format and their indices.
    Returns:
        Nothing
    """
    if len(faulty_lines) == 0:
        logging.info('    No issues.')
        return

    logging.info(f'Required number of values: {column_count:>{MAX_DIGITS}}\n'
                 f'           Line | # Values')
    for i, line in faulty_lines:
        logging.info(f'     {i + INDEX_SHIFT:<{MAX_DIGITS + 4}} | {len(line):>{MAX_DIGITS}}')


def check_content_format(sfdb):
    """Checks whether each line in the SFDB file that isn't a line of
        the header has the correct amount of values aka number of cells.
        Each line must have as many cells as there are columns specified
        in the header.

    Parameters:
        sfdb (SFDBContainer): The SFDB file.
    Returns:
        list: List of tuples (i(int), line(string)) containing the index
            of a line with wrong number of values in the sfdb_line_list as
            well as the line itself.
    """
    num_columns = len(sfdb.columns)
    return [(i, line) for i, line in enumerate(sfdb.content) if not len(line) == num_columns]


def log_excel_autoformatting_check(formatted_cells_list):
    """Logs the result of a check whether an sfdb had entries with signs of excel autoformatting.
    Parameters:
        formatted_cells_list (list(int, int, string): The lines with excel autoformatting, their indices for entry and
            affected column
    Returns:
        Nothing
    """
    if len(formatted_cells_list) == 0:
        logging.info('    No issues.')
        return

    faulty_lines_table_header = '      ' + (' ' * MAX_DIGITS) + 'Line | Entry'
    logging.info(faulty_lines_table_header)
    for i_row, i_col, line in formatted_cells_list:
        line_string = _list_to_string(line)
        logging.info(f'      {i_row + INDEX_SHIFT:>{MAX_DIGITS + 4}} | {line_string}')


def check_excel_autoformatting(sfdb):
    """Checks whether any value in an SFDB file is a number that was
    automatically formatted by excel (e.g. 1 000 000 000) to
    scientific notation (1E+9).

    Parameters:
        sfdb (SFDBContainer): The SFDB file.
    Returns:
        list: List of tuples (i (int),j (int), line(str)).
                i: index of line of value with excel-format warning
                j: index of column of value with excel-format warning
                line : The line with the value with excel-format warning.
    """
    content_lines = sfdb.content
    excel_formatted_cells = []
    for i, line in enumerate(content_lines):
        for j, column in enumerate(line):
            cell_value = str(column)
            if re.search(r'\dE\+\d', cell_value) is not None:
                excel_formatted_cells.append((i, j, line))
    return excel_formatted_cells


def log_duplicates_check(duplicates_list):
    """Logs the result of a check whether an sfdb had a duplicates.
    Parameters:
        duplicates_list (list(list(int), string)): A list of indices that share an identical line as well as the
            line itself.
    Returns:
        Nothing
    """
    if len(duplicates_list) == 0:
        logging.info('    No issues.')
        return

    logging.info(f'    First Occurrence | Duplicate Indices')
    for indices, line in duplicates_list:
        indices = [i + INDEX_SHIFT for i in indices]
        logging.info(f'    {indices[0]:>{MAX_DIGITS + 6}} | {_list_to_string(indices[1:])}\n'
                     f'    Entry: \'{_list_to_string(line)}\'')


def check_for_duplicates(sfdb):
    """Checks whether an SFDB file has duplicate lines.

    Parameters:
        sfdb (SFDBContainer): The SFDB file.
    Returns:
        list (list(int), str) : List of indices with identical entries and the entry itself. Line-indices start from 0.
    """
    return sfdb.get_duplicates()


def log_regex_check(non_regex_lines, regex_pattern):  # TODO: Hier muss noch explizit am Format gefeilt werden
    """Logs the result of a check whether an sfdb had a valid header
    Parameters:
        non_regex_lines (list(int, string)): A list of lines that didn't match the regular expression in regex_pattern
            and their indices in the file.
        regex_pattern (Pattern): A re.Pattern object of the regular expression that was searched for.
    Returns:
        Nothing
    """
    if len(non_regex_lines) == 0:
        logging.info('    No issues.')
        return
    logging.info(f'    Regex: \"{str(regex_pattern)[12:-2]}\":')
    logging.info(f'          Line | Entry')
    for i, line in non_regex_lines:
        logging.info(f'        {i + INDEX_SHIFT:>{MAX_DIGITS}} | {_list_to_string(line)}')


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


def log_datatype_check(non_conform_lines):
    """Logs the result of a check whether an sfdb had a valid header
    Parameters:
        non_conform_lines (): A list of entries where 1 or more values did not conform with their column's datatype.
    Returns:
        Nothing
    """
    if non_conform_lines is None:
        logging.info('    No Column Definitions found. Test skipped')
        return
    elif len(non_conform_lines) == 0:
        logging.info('    No issues.')
        return

    logging.info('    ' + (' ' * MAX_DIGITS) + 'Line-index | Column | Issue             | Entry')
    for (i, column_index, content_line, has_illegal_null, entry_not_match, length) in non_conform_lines:
        i += INDEX_SHIFT
        if has_illegal_null:
            content_string = _list_to_string(content_line)
            logging.info(f'     {i:<10} | {column_index + 1:<6} | "null" not allowed in column !       | '
                         f'{content_string}')
        elif entry_not_match:
            content_string = _list_to_string(content_line)
            logging.info(f'     {i:<10} | {column_index + 1:<6} | Value has incorrect length {length}! | '
                         f'{content_string}')
        else:
            content_string = _list_to_string(content_line)
            logging.info(f'     {i:<10} | -      | Unknown Error                        | {content_string}')


def check_datatype_conformity(sfdb):
    """Tests whether all values/cells in an SFDB file are in accordance
    with the datatype of the values column in the corresponding SQL
    table.

    Parameters:
        sfdb (SFDBContainer): The SFDB file
    Returns:
        list: A list of tuples (line_index (int), column_index (int),
            content_line(string), has_illegal_null (bool),
            entry_not_match (bool), length (int)).
            line_index: The index of the line where the datatype warning
                occurred
            column_index: The index of the column where the datatype
                warning occurred
            has_illegal_null: True if warning was caused by null in a
                column that does not allow null values.
            entry_not_match: True if warning was caused by an entry not
                matching the datatype or being too long for the column.
            length: The amount of characters allowed in the column that
                caused the warning.
    """
    warning_counter = 0

    if not sfdb.has_schema():
        return None

    list_of_issues = []
    for i, column_name in enumerate(sfdb.columns):
        column = sfdb.schema[column_name]
        regex_pattern = sfdb.schema.get_datatype_regex_pattern(
            column_name)  # Returns None if datatype is not known to function

        if regex_pattern is None:  # if datatype is not known to function, skip comparison
            logging.info(f'    Skipped comparison! {column_name} has unknown datatype {column.datatype}.')
            warning_counter += 1
            continue

        for j, line in enumerate(sfdb.content):
            cell_value = line[i]

            has_illegal_null = not column.with_null and cell_value is None
            entry_not_match = (len(cell_value) > column.length or not regex_pattern.search(cell_value))

            if has_illegal_null or entry_not_match:
                line_string = sfdb._seq_to_sfdb_line(line)
                list_of_issues.append((j, i, line_string, has_illegal_null, entry_not_match, column.length))

    return list_of_issues


def log_sfdb_comparison(diverging_lines):
    if diverging_lines is None:
        logging.info(
            '    Unable to do Comparison Test. Files did not have equal lengths with the given lines excluded.')
        return
    elif len(diverging_lines) == 0:
        logging.info('    No issues.')
        return

    for i_new, line_new, i_old, line_old in diverging_lines:
        logging.info(f'    !DEVIATION WARNING! :\n'
                     f'    Old line {i_old + INDEX_SHIFT:<{MAX_DIGITS}}: {line_old}\n'
                     f'    New line {i_new + INDEX_SHIFT:<{MAX_DIGITS}}: {line_new}')


def check_sfdb_comparison(sfdb_new, sfdb_old, excluded_lines_new=(), excluded_lines_old=(), excluded_columns=()):
    """Checks whether the lines of 2 SFDB files are identical after
    exclusion of specific lines and columns.

    Excluded lines and columns are specified via user-input. All lines
    that aren't identical cause a warning. All warnings are logged and
    the number of warnings returned.

    Parameters:
        sfdb_new (SFDBContainer): The updated version of an SFDB file.
        sfdb_old (SFDBContainer): The previous version of an SFDB file.
        excluded_lines_new (list): List of entry indices from sfdb_new that shall not be compared.
        excluded_lines_old (list): List of entry indices from sfdb_old that shall not be compared.
        excluded_columns (list): List of strings. The columns that shall be ignored for the comparison.
    Returns:
        int: Number of warnings raised.
    """
    logging.info(f'    Excluded lines in Old? {excluded_lines_old}')
    logging.info(f'    Excluded lines in New? {excluded_lines_new}')
    logging.info(f'    Excluded columns?      {excluded_columns}')

    # Change indices from (start at 1) to (start at 0)
    if excluded_lines_new is not None:
        excluded_lines_new = [i - INDEX_SHIFT for i in excluded_lines_new]
    if excluded_lines_old is not None:
        excluded_lines_old = [i - INDEX_SHIFT for i in excluded_lines_old]

    if not sfdb_new.name == sfdb_old.name:
        logging.info('    !DEVIATION WARNING! SQL Tables do not have the same name.')

    deviating_lines = _compare_sfdb_lines(sfdb_new, sfdb_old, excluded_lines_new, excluded_lines_old, excluded_columns)
    return deviating_lines


def _list_to_string(input_list):
    """Turns a list into a more easily human readable string"""
    if type(input_list) == np.ndarray:
        input_list = input_list.astype(str)
    return '   '.join(input_list)


def _compare_sfdb_lines(sfdb_new, sfdb_old, i_ex_lines_new, i_ex_lines_old, excluded_columns):
    """Checks whether the lines of 2 SFDB files are identical after
    exclusion of specific lines and columns.

    Compares SFDB header and content separately, as column-exclusion
    only matters for the SFDB's content.
    Raises a ComparisonError if the SFDB files don't have identical
    numbers of lines after exclusion of the specified lines.
    Loops over SFDB content and first checks every iteration whether
    a line in sfdb_new or sfdb_old must be skipped.

    Parameters:
        sfdb_new (SFDBContainer): The updated version of an SFDB file.
        sfdb_old (SFDBContainer): The previous version of an SFDB file.
        i_ex_lines_new (list): List of int. Line-indices to be excluded from sfdb_new
        i_ex_lines_old (list): List of int. Line-indices to be excluded from sfdb_old
        excluded_columns (list): List of strings. Names columns to be
            excluded from both sfdb files.
    Returns:
        list: List of tuples (i (int), j (int)).
                i: Index of deviating line in sfdb_new
                j: Index of deviating line in sfdb_old
    """
    if not len(sfdb_new) - len(i_ex_lines_new) == len(sfdb_old) - len(i_ex_lines_old):
        raise ComparisonError('Can not compare SFDB files with unequal number of lines!')

    i_ex_col_new = []
    i_ex_col_old = []
    if excluded_columns is not None:
        i_ex_col_new = [sfdb_new.columns.index(col) for col in excluded_columns if col in sfdb_new.columns]
        i_ex_col_old = [sfdb_old.columns.index(col) for col in excluded_columns if col in sfdb_old.columns]
    deviating_lines = [(i, sfdb_new.header[i], i, sfdb_old.header[i]) for i in range(len(sfdb_new.header))
                       if not sfdb_new.header[i] == sfdb_old.header[i]]

    i = 0
    j = 0
    while i in range(len(sfdb_new)) and j in range(len(sfdb_old)):
        if i in i_ex_lines_new:
            i += 1
            continue

        if j in i_ex_lines_old:
            j += 1
            continue

        is_equal = _compare_line(sfdb_new[i], sfdb_old[j], i_ex_col_new, i_ex_col_old)
        if not is_equal:
            deviating_lines.append((i, sfdb_new.get_entry_string(i), j, sfdb_old.get_entry_string(j)))
        i += 1
        j += 1

    return deviating_lines


def _compare_line(new_line, old_line, i_ex_col_new, i_ex_col_old):
    """Checks whether 2 lines of different SFDB files are identical or not.

    Loops over the values and compares column by column. Checks every
    iteration first whether a column in the new or the old line must be skipped.
    Raises a ComparisonError if the lines don't have identical
    numbers of columns after exclusion of the specified columns.

    Parameters:
        new_line(list): List of strings. A line from an updated SFDB file.
        old_line(list): List of strings. A line from the previous SFDB file.
        i_ex_col_new(list): List of int. Indices of columns in new_line that
            are excluded from the comparison.
        i_ex_col_old(list): List of int. Indices of columns in old_line that
            are excluded from the comparison.
    Returns:
        bool: True if lines are identical. False if they are not.
    """
    if not len(new_line) - len(i_ex_col_new) == len(old_line) - len(i_ex_col_old):
        raise ComparisonError(f'Can not compare SFDB lines with unequal number of values!\n'
                              f'Line new: {new_line}\nLine old: {old_line}\n'
                              f'Excluded Columns 1: {i_ex_col_new}\n'
                              f'Excluded Columns 2: {i_ex_col_old}')

    i = 0
    j = 0
    while i < len(new_line) and j < len(old_line):
        if i_ex_col_new is not [] and i in i_ex_col_new:
            i += 1
            continue

        if i_ex_col_old is not [] and j in i_ex_col_old:
            j += 1
            continue

        if not new_line[i] == old_line[j]:
            return False

        i += 1
        j += 1

    return True
