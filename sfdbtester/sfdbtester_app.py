import logging
import sys
import os

from sfdbtester.common import argparser as ap
from sfdbtester.sfdb import sfdb_checks as sc
from sfdbtester.common.sfdb_logging import LOGFILE_LEVEL, create_log_filepath, configurate_logger

# TODO: For GUI - make a button that opens a window that allows adding, editing and deleting of SFDB schemas


def run():
    # Initialize logging
    sfdb_path = os.path.abspath(sys.argv[1])
    log_filepath = create_log_filepath(sfdb_path)
    configurate_logger(log_filepath)

    logging.log(LOGFILE_LEVEL, f'LOG FILE FOR SFDB FILE : {sfdb_path}')
    logging.log(LOGFILE_LEVEL, 'Indices in this log start from 1\n')

    warning_counter = 0

    # Receive Arguments
    args = ap.parse_args(sys.argv[1:])
    if args.request:
        args = ap.request_missing_args(args)

    # Perform Tests on SFDB file
    logging.log(LOGFILE_LEVEL, 'STARTING CONTENT FORMAT TEST')
    wrong_format_entries = sc.check_content_format(args.SFDBFile)
    sc.log_sfdb_content_format_check(len(args.SFDBFile.columns), wrong_format_entries)
    logging.log(LOGFILE_LEVEL, 'FINISHED CONTENT FORMAT TEST\n')

    # Run tests that crash if SFDB file has format issues
    if not wrong_format_entries:
        logging.log(LOGFILE_LEVEL, 'STARTING EXCEL AUTOFORMATTING TEST')
        formatted_cells_list = sc.check_excel_autoformatting(args.SFDBFile)
        sc.log_excel_autoformatting_check(formatted_cells_list)
        warning_counter += len(formatted_cells_list)
        logging.log(LOGFILE_LEVEL, 'FINISHED EXCEL AUTOFORMATTING TEST\n')

        logging.log(LOGFILE_LEVEL, 'STARTING DUPLICATE TEST')
        duplicates = args.SFDBFile.get_duplicates()
        sc.log_duplicates_check(duplicates)
        warning_counter += len(args.SFDBFile._get_duplicate_index_list())
        logging.log(LOGFILE_LEVEL, 'FINISHED DUPLICATE TEST\n')

        logging.log(LOGFILE_LEVEL, 'STARTING DATATYPE TEST')
        non_conform_entries = sc.check_datatype_conformity(args.SFDBFile)
        sc.log_datatype_check(non_conform_entries)
        warning_counter += 0 if non_conform_entries is None else len(non_conform_entries)
        logging.log(LOGFILE_LEVEL, 'FINISHED  DATATYPE TEST\n')

        if args.regular_expression:
            logging.log(LOGFILE_LEVEL, 'STARTING REGEX TEST')
            non_regex_entries = sc.check_content_against_regex(args.SFDBFile, args.regular_expression)
            sc.log_regex_check(non_regex_entries, args.regular_expression)
            warning_counter += len(non_regex_entries)
            logging.log(LOGFILE_LEVEL, 'FINISHED REGEX TEST\n')

        if args.comparison_sfdb:
            logging.log(LOGFILE_LEVEL, 'STARTING COMPARISON TEST')
            diverging_entries = sc.check_sfdb_comparison(args.SFDBFile,
                                                       args.comparison_sfdb,
                                                       args.ex_lines1,
                                                       args.ex_lines2,
                                                       args.ex_col)
            sc.log_sfdb_comparison(diverging_entries)
            warning_counter += len(diverging_entries)
            logging.log(LOGFILE_LEVEL, 'FINISHED COMPARISON TEST\n')

        if args.write:
            no_dupl_sfdb_file = args.SFDBFile[:-5] + '_no_duplicates.sfdb'
            logging.log(LOGFILE_LEVEL, 'Writing SFDB file without duplicates to {no_dupl_sfdb_file}')
            args.SFDBFile.write(no_dupl_sfdb_file, sort=args.sorted, remove_duplicates=True)

    else:
        logging.info('Only format tests were carried out due to the format issues.\n'
                     'Please run this software again after fixing them.')

    # Finish logging
    logging.log(LOGFILE_LEVEL, 'Done')
    logging.info(f'The file caused {warning_counter} warning-messages.')
    logging.info(f'Logfile written to {log_filepath}.\nDone')


if __name__ == '__main__':
    run()
