import logging

from sfdbtester.common.argparser import get_args
from sfdbtester.sfdb import sfdb_checks as sc
from sfdbtester.sfdb.sfdb import SFDBContainer
from sfdbtester.common.sfdb_logging import LOGFILE_LEVEL, create_log_filepath, configurate_logger


def run():
    args = get_args()

    # Initialize logging
    log_filepath = create_log_filepath(args.SFDBFile)
    configurate_logger(log_filepath)

    logging.log(LOGFILE_LEVEL, f'LOG FILE FOR SFDB FILE : {args.SFDBFile}')
    logging.log(LOGFILE_LEVEL, 'Indices in this log start from 1\n')

    warning_counter = 0

    # Get SFDB File Object
    sfdb_new = SFDBContainer.from_file(args.SFDBFile)

    # Perform Tests on SFDB file
    logging.log(LOGFILE_LEVEL, 'STARTING CONTENT FORMAT TEST')
    wrong_format_lines = sc.check_content_format(sfdb_new)
    sc.log_sfdb_content_format_check(len(sfdb_new.columns), wrong_format_lines)
    logging.log(LOGFILE_LEVEL, 'FINISHED CONTENT FORMAT TEST\n')

    # Run tests that crash if SFDB file has format issues
    if not wrong_format_lines:
        logging.log(LOGFILE_LEVEL, 'STARTING EXCEL AUTOFORMATTING TEST')
        formatted_cells_list = sc.check_excel_autoformatting(sfdb_new)
        sc.log_excel_autoformatting_check(formatted_cells_list)
        warning_counter += len(formatted_cells_list)
        logging.log(LOGFILE_LEVEL, 'FINISHED EXCEL AUTOFORMATTING TEST\n')

        logging.log(LOGFILE_LEVEL, 'STARTING DUPLICATE TEST')
        duplicates = sfdb_new.get_duplicates()
        sc.log_duplicates_check(duplicates)
        warning_counter += len(sfdb_new._get_duplicate_index_list())
        logging.log(LOGFILE_LEVEL, 'FINISHED DUPLICATE TEST\n')

        logging.log(LOGFILE_LEVEL, 'STARTING DATATYPE TEST')
        non_conform_lines = sc.check_datatype_conformity(sfdb_new)
        sc.log_datatype_check(non_conform_lines)
        warning_counter += 0 if non_conform_lines is None else len(non_conform_lines)
        logging.log(LOGFILE_LEVEL, 'FINISHED  DATATYPE TEST\n')

        if args.re:
            logging.log(LOGFILE_LEVEL, 'STARTING REGEX TEST')
            non_regex_lines = sc.check_content_against_regex(sfdb_new, args.regular_expression)
            sc.log_regex_check(non_regex_lines, args.re)
            warning_counter += len(non_regex_lines)
            logging.log(LOGFILE_LEVEL, 'FINISHED REGEX TEST\n')

        if args.comparison_sfdb:
            logging.log(LOGFILE_LEVEL, 'STARTING COMPARISON TEST')
            sfdb_old = SFDBContainer.from_file(args.comparison_sfdb)
            diverging_lines = sc.check_sfdb_comparison(sfdb_new, sfdb_old, args.ex_lines1, args.ex_lines2, args.ex_col)
            sc.log_sfdb_comparison(diverging_lines)
            warning_counter += len(diverging_lines)
            logging.log(LOGFILE_LEVEL, 'FINISHED COMPARISON TEST\n')

        if args.write:
            no_dupl_sfdb_file = args.SFDBFile[:-5] + '_no_duplicates.sfdb'
            logging.log(LOGFILE_LEVEL, 'Writing SFDB file without duplicates to {no_dupl_sfdb_file}')
            sfdb_new.write(no_dupl_sfdb_file, sort=args.sorted, remove_duplicates=True)

    else:
        logging.info('Only format tests were carried out due to the format issues.\n'
                     'Please run this software again after fixing them.')

    # Finish logging
    logging.log(LOGFILE_LEVEL, 'Done')
    logging.info(f'The file caused {warning_counter} warning-messages.')
    logging.info(f'Logfile written to {log_filepath}.\nDone')


if __name__ == '__main__':
    run()
