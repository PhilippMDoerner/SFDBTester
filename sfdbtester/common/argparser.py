import argparse
import os
import re
from sfdbtester.common import userinput as ui


def exclusion_index(arg):
    arg = int(arg)
    if arg <= 0:
        raise argparse.ArgumentTypeError(f"The index {arg} is invalid ! Negative Indices are not allowed!")
    if arg <= 5:
        raise argparse.ArgumentTypeError(f"The index {arg} is invalid ! Index must be larger than 5")
    return arg


def filepath(arg):
    if not os.path.isfile(arg):
        argparse.ArgumentTypeError(f'The file {arg} does not exist!')
    else:
        return arg


def regex(arg):
    try:
        regex_pattern = re.compile(arg, re.IGNORECASE)
        return regex_pattern
    except re.error:
        raise argparse.ArgumentTypeError(f"The expression {arg} is not valid regular expression")


def get_args():
    parser = argparse.ArgumentParser(description='Test SFDB files for errors')
    parser.add_argument('SFDBFile', type=filepath,
                        help='Filepath to the SFDB file')
    parser.add_argument('-re', type=regex,
                        help='Regular Expression to check the SFDB file')
    parser.add_argument('-c',  '--comparison_sfdb', type=filepath,
                        help='Filepath to a second SFDB file to compare to the first')
    parser.add_argument('-x1', '--ex_lines1', default=[], type=exclusion_index, nargs='+',
                        help='Indices of lines in first SFDB file to exclude from comparison with second SFDB file. '
                               'Header lines can not be excluded, thus the minimum index is 6.')
    parser.add_argument('-x2', '--ex_lines2', default=[], type=exclusion_index, nargs='+',
                        help='Indices of lines in second SFDB file to exclude from comparison with first SFDB file. '
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

    cmd_args = parser.parse_args()
    if cmd_args.request:
        cmd_args = request_missing_args(cmd_args)
    return cmd_args


def request_missing_args(cmd_args):
    # Request -re Regex
    if cmd_args.re is None:
        cmd_args.re = ui.request_regex_pattern("Please enter a regular expression matching SFDB lines (optional):\n")
    # Request -c Filepath
    if cmd_args.comparison_sfdb is None:
        cmd_args.comparison_sfdb = ui.request_filepath('Path to old SFDB file for comparison tests (optional):\n')
    # Request -x1 exclusion row indices
    if cmd_args.ex_lines1 is None and cmd_args.comparison_sfdb is not None:
        input_message = ("\tPlease enter the indices of all lines in the old SFDB "
                         "(starting from 1) that were removed, separated by "
                         "spaces (optional):\n\t")
        cmd_args.ex_lines1 = ui.request_list_of_int(input_message, min_value=6)

    # Request -x2 eclusion row indices
    if cmd_args.ex_lines2 is None and cmd_args.comparison_sfdb is not None:
        input_message = ("\tPlease enter the indices of all lines in the new SFDB "
                         "(starting from 1) that were added, separated by spaces"
                         " (optional):\n\t")
        cmd_args.ex_lines2 = ui.request_list_of_int(input_message, min_value=6)

    # Request -xc eclusion column names
    if cmd_args.ex_col is None and cmd_args.comparison_sfdb is not None:
        input_message = ('\tPlease enter the name of all columns you wish to '
                         'ignore for the comparison, separated by spaces '
                         '(optional):\n\t')
        cmd_args.ex_col = input(input_message).split()

    return cmd_args


if __name__ == '__main__':
    cmd_args = get_args()
    print(cmd_args)
    for key in cmd_args.__dict__:
        print(f'{key:<15} : {cmd_args.__dict__[key]}')
