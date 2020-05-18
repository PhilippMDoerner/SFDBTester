import re
import logging
from sfdbtester.common import userinput as ui
import numpy as np
from sfdbtester.sfdb.sfdb import SFDBContainer

MAX_DIGITS = 10

#TODO: Separate checking and logging of all tests
#TODO: Throw all checks together in a single big test

class ComparisonError(Exception):
    pass


def log_sfdb_header_check(has_valid_header):
    """Tests the format of an SFDB file's header
    Parameters:
        sfdb (SFDBContainer): The SFDB file.
    Returns:
        int: The number of all lines that raised warnings.
    """
    logger = logging.getLogger('main')

    if not has_valid_header:
        logger.info('    !HEADER FORMAT WARNING! There is a format error within the first 5 lines of the SFDB')


def log_sfdb_content_format_check(column_count, faulty_lines):
    logger = logging.getLogger('main')

    if len(faulty_lines) == 0:
        logger.info('    No issues.')
        return

    logger.info(f'Required number of values: {column_count:>{MAX_DIGITS}}\n'
                f'           Line | # Values')
    for i, line in faulty_lines:
        logger.info(f'     {i+1:<{MAX_DIGITS+4}} | {len(line):>{MAX_DIGITS}}')


def log_excel_autoformatting_check(formatted_cells_list):#TODO: Have the output explicitly show the value with the issue
    logger = logging.getLogger('main')

    if len(formatted_cells_list) == 0:
        logger.info('    No issues.')
        return

    faulty_lines_table_header = '      '+(' '*MAX_DIGITS)+'Line | Entry'
    logger.info(faulty_lines_table_header)
    for i_row, i_col, line in formatted_cells_list:
        line_string = _list_to_string(line)
        logger.info(f'      {i_row + 1:>{MAX_DIGITS+4}} | {line_string}')


def log_duplicates_check(duplicates_list):
    logger = logging.getLogger('main')

    if len(duplicates_list) == 0:
        logger.info('    No issues.')
        return

    logger.info(f'    First Occurrence | Duplicate Indices')
    for indices, line in duplicates_list:
        logger.info(f'    {indices[0]:>{MAX_DIGITS+6}} | {_list_to_string(indices[1:])}\n'
                    f'    Entry: \'{_list_to_string(line)}\'')


def test_sfdb_format(sfdb):
    """Tests the format of all lines in an SFDB file.

    Tests each line whether it is in accordance with the standard SFDB
    format, whether it was likely modified by excel and whether there
    are any duplicates of it in the SFDB file. Logs any lines with
    format issues and counts the number of lines with format issues.

    Parameters:
        sfdb (SFDBContainer): The SFDB file.
    Returns:
        int: The number of all lines that raised warnings.
    """
    logger = logging.getLogger('main')
    warning_counter = 0

    logger.info('STARTING HEADER TEST')
    has_valid_header = check_header_format(sfdb)
    log_sfdb_header_check(has_valid_header)
    warning_counter += 1 if has_valid_header else 0
    logger.info('FINISHED HEADER TEST\n')

    logger.info('STARTING CONTENT FORMAT TEST')
    wrong_content_lines = check_content_format(sfdb)
    log_sfdb_content_format_check(len(sfdb.columns), wrong_content_lines)
    warning_counter += len(wrong_content_lines)
    logger.info('FINISHED CONTENT FORMAT TEST\n')

    logger.info('STARTING EXCEL AUTOFORMATTING TEST')
    formatted_cells_list = check_excel_autoformatting(sfdb)
    log_excel_autoformatting_check(formatted_cells_list)
    warning_counter += len(formatted_cells_list)
    logger.info('FINISHED EXCEL AUTOFORMATTING TEST\n')

    logger.info('STARTING DUPLICATE TEST')
    duplicates = sfdb.get_duplicates()
    log_duplicates_check(duplicates)
    warning_counter += len(sfdb._get_duplicate_index_list())
    logger.info('FINISHED DUPLICATE TEST\n')

    return warning_counter


def log_regex_check(non_regex_lines, regex_pattern):#TODO: Hier muss noch explizit am Format gefeilt werden
    logger = logging.getLogger('main')

    if len(non_regex_lines) == 0:
        logger.info('    No issues.')
        return

    logger.info(f'    Regex: \"{str(regex_pattern)[12:-2]}\":')
    logger.info(f'          Line | Entry')
    for i, line in non_regex_lines:
        logger.info(f'        {i + 1:>{MAX_DIGITS}} | {_list_to_string(line)}')


def test_sfdb_against_regex(sfdb, regex_pattern):
    """Tests all lines in an SFDB file whether they match a regular expression.

    The regular expression is provided by user input. Logs and counts all lines
    that did not match the expression.

    Parameters:
        sfdb (SFDBContainer): The SFDB file.
        regex_pattern : The regular expression each sfdb entry has to conform to
    Returns:
        int: The number of all lines that did not contain the regular
            expression.
    """
    logger = logging.getLogger('main')

    logger.info('STARTING REGEX TEST')
    non_regex_lines = check_content_against_regex(sfdb, regex_pattern)
    log_regex_check(non_regex_lines, regex_pattern)
    warning_counter = len(non_regex_lines)
    logger.info('FINISHED REGEX TEST')

    return warning_counter


def test_sfdb_datatypes(sfdb):
    """Tests the datatype compliance of all values in an SFDB file with
    their corresponding SQL table.

    Lines with values that are not compliant with their column's SQL definition
    (e.g. do not match date when datatype is "datetime", contain "null" when
    column does not allow null or contain 6 characters when 5 is the limit).
    SQL Table column definitions are gained from the SQLTableSchema Object
    within the given SFDBContainer object.

    Parameters:
        sfdb (SFDBContainer): The SFDB file.
    Returns:
        int: The number of lines that raised warnings.
    """
    logger = logging.getLogger('main')
    warning_counter = 0

    if sfdb.has_schema():
        non_conform_lines = check_datatype_conformity(sfdb)

        for (i, column_index, content_line, has_illegal_null, entry_not_match, length) in non_conform_lines:
            if has_illegal_null:
                content_string = _list_to_string(content_line)
                logger.info(f'\t!DATATYPE WARNING! Line {i + 1:<10} Column '
                            f'{column_index + 1:<3} has a "null" value where '
                            f'"null" is not allowed: {content_string}')
            elif entry_not_match:
                content_string = _list_to_string(content_line)
                logger.info(f'\t!DATATYPE WARNING! Line {i + 1:<10} Column '
                            f'{column_index + 1:<3} does not match its datatype with length '
                            f'{length} : {content_string}')
            else:
                content_string = _list_to_string(content_line)
                logger.info(f'\t!DATATYPE WARNING! Line {i:<10} Unknown Error  : {content_string}')

        warning_counter += len(non_conform_lines)
    else:
        logger.info('\tNo Column Definitions found. Test skipped')

    return warning_counter


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
    logger = logging.getLogger('main')
    warning_counter = 0

    list_of_issues = []
    for i, column_name in enumerate(sfdb.columns):
        column = sfdb.schema[column_name]
        regex_pattern = sfdb.schema.get_datatype_regex_pattern(column_name)  # Returns None if datatype is not known to function

        if regex_pattern is None:  # if datatype is not known to function, skip comparison
            logger.info(f'\tSkipped comparison for {column_name} due to '
                        f'{column.datatype} being an unknown datatype.')
            warning_counter += 1
            continue

        for j, line in enumerate(sfdb.content):
            cell_value = line[i]
            has_illegal_null = not column.with_null and cell_value is None
            entry_not_match = (len(cell_value) > column.length or not regex_pattern.search(cell_value))

            if has_illegal_null or entry_not_match:
                list_of_issues.append((j + 5, i, line, has_illegal_null, entry_not_match, column.length))

    return list_of_issues


def compare_sfdb_files(sfdb_new, sfdb_old, excluded_lines_new, excluded_lines_old, excluded_columns):
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
    logger = logging.getLogger('main')
    warning_counter = 0

    logger.info('\tExcluded lines in Old? {}'.format(excluded_lines_old))
    logger.info('\tExcluded lines in New? {}'.format(excluded_lines_new))
    logger.info('\tExcluded columns?      {}'.format(excluded_columns))

    # Change indices from (start at 1) to (start at 0)
    if excluded_lines_new is not None:
        excluded_lines_new = [i - 1 for i in excluded_lines_new]
    if excluded_lines_old is not None:
        excluded_lines_old = [i - 1 for i in excluded_lines_old]

    if not sfdb_new.name == sfdb_old.name:
        logger.info('\t!DEVIATION WARNING! SQL Tables do not have the same name.')
        warning_counter += 1

    deviating_lines = _compare_sfdb_lines(sfdb_new, sfdb_old, excluded_lines_new, excluded_lines_old, excluded_columns)
    if deviating_lines is None:
        warning_line = ('!WARNING! Files did not have equal lengths with the given lines excluded. '
                        'Comparison test was skipped.')
        logger.info('\t' + warning_line)
        print(warning_line)
    else:
        for i_new, i_old in deviating_lines:
            line_new = _list_to_string(sfdb_new[i_new])
            line_old = _list_to_string(sfdb_old[i_old])
            logger.info(f'\t!DEVIATION WARNING! :\n'
                        f'\tOld line {i_old + 1}: {line_old}\n'
                        f'\tNew line {i_new+1}: {line_new}')
        warning_counter += len(deviating_lines)

    return warning_counter


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
    deviating_lines_header = [(i, i) for i in range(len(sfdb_new.header))
                              if not sfdb_new.header[i] == sfdb_old.header[i]]

    deviating_lines_content = []
    i = 5
    j = 5
    while i in range(len(sfdb_new)) and j in range(len(sfdb_old)):
        if i in i_ex_lines_new:
            i += 1
            continue

        if j in i_ex_lines_old:
            j += 1
            continue

        is_equal = _compare_line(sfdb_new[i], sfdb_old[j], i_ex_col_new, i_ex_col_old)
        if not is_equal:
            deviating_lines_content.append((i, j))
        i += 1
        j += 1

    deviating_lines_content = [(i, j) for i, j in deviating_lines_content]
    return deviating_lines_header + deviating_lines_content


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


def check_header_format(sfdb):
    """Checks whether each line in the header of an SFDB file follows
    the SFDB format specifications."""
    header = sfdb.header
    is_correct_header = ((header[0][0] == 'ENCODING UTF8')  and (len(header[0]) == 1) and
                                (header[1][0] == 'INIT')    and (len(header[1]) == 1) and
                                (header[2][0] == 'TABLE')   and (len(header[2]) == 2) and
                                (header[3][0] == 'COLUMNS') and (len(header[3]) >  1) and
                                (header[4][0] == 'INSERT')  and (len(header[4]) == 1))
    return is_correct_header


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
    return [(i + 5, line) for i, line in enumerate(sfdb.content) if not len(line) == num_columns]


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
                excel_formatted_cells.append((i + 5, j, line))
    return excel_formatted_cells


def check_for_duplicates(sfdb):
    """Checks whether an SFDB file has duplicate lines.

    Parameters:
        sfdb (SFDBContainer): The SFDB file.
    Returns:
        list : List of tuples (i(int), j(int), line(str)). Each tuple is
            an occurrence of 2 identical lines at indices i and j in the sfdb file.
    """
    duplicate_lines = []
    for i, line1 in enumerate(sfdb):
        for j in range(i + 1, len(sfdb)):
            line2 = sfdb[j]
            if line1 == line2 and not line1 == "":
                duplicate_lines.append((i, j, line1))
    return duplicate_lines


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
        lines_without_regex = [(i + 5, line) for i, line in enumerate(sfdb_lines)
                               if not regex_pattern.search(str(line))]
    return lines_without_regex
