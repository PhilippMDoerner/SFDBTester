import argparse
import os
import re
import logging
from sfdbtester.common import userinput as ui
from sfdbtester.sfdb import sfdb

# TODO: Change the way the regex flag works. It shall accept pairs of 2 arguments - a column name and a regular
#  expression (check for them being valid inputs accordingly). It shall then be checked for each column whether every
#  value in that column conforms to that regular expression.


class WrongArgumentError(Exception):
    pass


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # self.print_help(sys.stderr)
        raise WrongArgumentError(message)


def exclusion_index(i):
    """Checks whether an index is a valid line-index of an entry in an SFDB file. Line indices start at 1. As SFDB
    headers take up the first 5 lines, the smallest allowed index is 6"""
    if i == '':
        raise WrongArgumentError('argument -x1/ex_lines1 or -x2/ex_lines2: expected an argument, not an empty string')

    try:
        i = int(i)
    except ValueError:
        raise WrongArgumentError(f"argument -x1/--exclusion_index1 or -x2/--exclusion_index2: "
                                 f"\'{i}\' is not a number!")

    if i <= 0:
        raise WrongArgumentError(f"argument -x1/--exclusion_index1 or -x2/--exclusion_index2: "
                                 f"The index {i} is invalid ! Negative Indices are not allowed!")
    if 0 < i <= 5:
        raise WrongArgumentError(f"argument -x1/--exclusion_index1 or -x2/--exclusion_index2: "
                                 f"The index {i} is invalid ! Index must be larger than 5")
    return i


def sfdb_file(input_filepath):
    """Checks whether the filepath provided as argument leads to an actual file."""
    if input_filepath == '':
        raise WrongArgumentError('argument SFDBFile or -c/--comparison_sfdb: expected one argument')

    elif os.path.isdir(input_filepath):
        raise WrongArgumentError(f'argument SFDBFile or -c/--comparison_sfdb: '
                                 f'\'{input_filepath}\' is a directory!')

    elif not os.path.isfile(input_filepath):
        raise WrongArgumentError(f'argument SFDBFile or -c/--comparison_sfdb: '
                                 f'The file \'{input_filepath}\' does not exist!')
    else:
        return sfdb.SFDBContainer.from_file(input_filepath)


def regex(arg):
    """Checks whether the regular expression provided as argument is a valid regular expression."""
    if arg is None:
        raise WrongArgumentError('argument -re/--regular_expression: expected one argument')
    try:
        regex_pattern = re.compile(arg, re.IGNORECASE)
        return regex_pattern
    except re.error:
        raise WrongArgumentError(f"argument -re/--regular_expression: "
                                 f"\'{arg}\' is not a valid regular expression!")


def parse_args(args):
    parser = ArgumentParser(description='Test SFDB files for errors')
    parser.add_argument('SFDBFile', type=sfdb_file,
                        help='Filepath to the SFDB file')
    parser.add_argument('-re', '--regular_expression', type=regex,
                        help='Regular Expression to check the SFDB file')
    parser.add_argument('-c',  '--comparison_sfdb', type=sfdb_file, default=None,
                        help='Filepath to a second SFDB file to compare to the first')
    parser.add_argument('-x1', '--ex_lines1', default=[], type=exclusion_index, nargs='+',
                        help='Indices of lines in new SFDB file to exclude from comparison with second SFDB file. '
                               'Header lines can not be excluded, thus the minimum index is 6.')
    parser.add_argument('-x2', '--ex_lines2', default=[], type=exclusion_index, nargs='+',
                        help='Indices of lines in old SFDB file to exclude from comparison with first SFDB file. '
                               'Header lines can not be excluded, thus the minimum index is 6.')
    parser.add_argument('-xc', '--ex_col', default=[], type=str, nargs='+',
                        help='Names of columns occurring in first or second SFDB file to exclude from their '
                               'comparison')
    parser.add_argument('-w', '--write', action='store_true',
                        help='If SFDB file contains duplicates, write new SFDB file without duplicates')
    parser.add_argument('-s',  '--sorted', action='store_true',
                        help='Sorts line of SFDB file before writing with -w')
    parser.add_argument('-r',  '--request', action='store_true',
                        help='If enabled requests command line arguments individually via user-input')

    parsed_args = parser.parse_args(args)
    _check_excluded_line_indices(parsed_args.ex_lines1, parsed_args.SFDBFile)
    _check_excluded_line_indices(parsed_args.ex_lines2, parsed_args.comparison_sfdb)
    _check_excluded_columns(parsed_args.ex_col, parsed_args.SFDBFile, parsed_args.comparison_sfdb)

    return parsed_args


def _check_excluded_line_indices(index_list_for_sfdb, args_sfdb):
    if not index_list_for_sfdb:
        return

    invalid_indices = [i for i in index_list_for_sfdb if i >= len(args_sfdb.sfdb_lines)]
    if invalid_indices:
        raise WrongArgumentError(f'argument -x1/--exclusion_index1 or -x2/--exclusion_index2: '
                                 f'Indices {invalid_indices} are out of bounds for {args_sfdb.name} with '
                                 f'{len(args_sfdb.sfdb_lines)} lines!')


def _check_excluded_columns(excluded_columns, sfdb1, sfdb2):
    if not excluded_columns:
        return

    if not sfdb2:
        raise WrongArgumentError('argument -xc/-ex_col: Can not use argument -xc without argument -c')

    invalid_columns = [col for col in excluded_columns if (col not in sfdb1.columns or col not in sfdb2.columns)]
    if invalid_columns:
        raise WrongArgumentError(f'argument -xc/-ex_col: '
                                 f'Table columns {invalid_columns} are not present in both {sfdb1.name} and '
                                 f'{sfdb2.name} !')


def request_missing_args(partial_args):
    """Sees which arguments are logically missing based on the already provided arguments and actively requests them
    from the user. """
    # Request -re Regex
    if partial_args.regular_expression is None:
        partial_args.regular_expression = ui.request_regex_pattern("Enter a regular expression matching "
                                                                    "SFDB lines (optional):\n")

    # Request -c Filepath
    if partial_args.comparison_sfdb is None:
        partial_args.comparison_sfdb = ui.request_sfdb('Path to old SFDB file for comparison tests (optional):\n')
    else:
        logging.info('Path to comparison-SFDB File has already been provided.')

    # Request -x1 exclusion row indices
    if partial_args.ex_lines1 == [] and partial_args.comparison_sfdb:
        input_message = ("\tEnter a space-separated list of the indices of all lines in the old SFDB (starting from 1) "
                         "that were removed (optional):\n"
                         "\t")
        partial_args.ex_lines1 = ui.request_list_of_int(input_message, min_value=6)

    # Request -x2 eclusion row indices
    if partial_args.ex_lines2 == [] and partial_args.comparison_sfdb:
        input_message = ("\tEnter a space-separated list of the indices of all lines in the new SFDB (starting from 1) "
                         "that were added, separated by spaces (optional):\n"
                         "\t")
        partial_args.ex_lines2 = ui.request_list_of_int(input_message, min_value=6)

    # Request -xc eclusion column names
    if partial_args.ex_col == [] and partial_args.comparison_sfdb:
        input_message = ('\tEnter a space-separated list of the name of the columns you wish to ignore for the '
                         'comparison (optional):\n'
                         '\t')
        partial_args.ex_col = input(input_message).split()

    return partial_args
