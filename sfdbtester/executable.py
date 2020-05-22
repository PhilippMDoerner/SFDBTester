import logging
from logging import config
from datetime import datetime

from sfdbtester.common.argparser import get_args
from sfdbtester.common.utilities import get_resource_filepath
from sfdbtester.sfdb import sfdb_checks as sc
from sfdbtester.sfdb.sfdb import SFDBContainer

"""def configurate_logger(log_filepath):
    LOG_FORMAT = "%(message)s"
    handler = logging.FileHandler(log_filepath, 'w', 'utf-8')
    logging.basicConfig(level=logging.DEBUG,
                        format=LOG_FORMAT,
                        handlers=[handler])"""


def configurate_logger(log_filepath):
    LOGFILE_LEVEL = 15
    logging.addLevelName(LOGFILE_LEVEL, 'LOGFILE')

    logging.log_filepath = log_filepath

    config_file = get_resource_filepath('logging.cfg')
    logging.config.fileConfig(config_file)


def create_log_filepath(sfdb_filename):
    now = f'{datetime.now():%y-%m-%d_%H%M%S}'
    log_filepath = f'{sfdb_filename[:-5]}_{now}_log.txt'
    return log_filepath


def execute_check(check_name, check_func, log_func, check_func_args, log_func_args):
    logging.info(f'STARTING {check_name} FORMAT TEST')
    faulty_lines = check_func(check_func_args)
    log_func(log_func_args)
    logging.info('fFINISHED {check_name} FORMAT TEST\n')
    return len(faulty_lines)


def run():
    args = get_args()

    # Initialize logging
    log_filepath = create_log_filepath(args.SFDBFile)
    configurate_logger(log_filepath)

    logging.info(f'LOG FILE FOR SFDB FILE : {args.SFDBFile}')
    logging.info('Indices in this log start from 1')

    warning_counter = 0

    # Get SFDB File Object
    sfdb_new = SFDBContainer.from_file(args.SFDBFile)

    # Perform Tests on SFDB file
    logging.info('STARTING CONTENT FORMAT TEST')
    wrong_content_lines = sc.check_content_format(sfdb_new)
    sc.log_sfdb_content_format_check(len(sfdb_new.columns), wrong_content_lines)
    warning_counter += len(wrong_content_lines)
    logging.info('FINISHED CONTENT FORMAT TEST\n')

    # TODO: Stop the program if formatting errors are encountered or somehow deal with them, e.g. deleting them from the sfdb

    logging.info('STARTING EXCEL AUTOFORMATTING TEST')
    formatted_cells_list = sc.check_excel_autoformatting(sfdb_new)
    sc.log_excel_autoformatting_check(formatted_cells_list)
    warning_counter += len(formatted_cells_list)
    logging.info('FINISHED EXCEL AUTOFORMATTING TEST\n')

    logging.info('STARTING DUPLICATE TEST')
    duplicates = sfdb_new.get_duplicates()
    sc.log_duplicates_check(duplicates)
    warning_counter += len(sfdb_new._get_duplicate_index_list())
    logging.info('FINISHED DUPLICATE TEST\n')

    logging.info('STARTING DATATYPE TEST')
    non_conform_lines = sc.check_datatype_conformity(sfdb_new)
    sc.log_datatype_check(non_conform_lines)
    warning_counter += 0 if non_conform_lines is None else len(non_conform_lines)
    logging.info('FINISHED  DATATYPE TEST')

    if args.re:
        logging.info('STARTING REGEX TEST')
        non_regex_lines = sc.check_content_against_regex(sfdb_new, args.re)
        sc.log_regex_check(non_regex_lines, args.re)
        warning_counter += len(non_regex_lines)
        logging.info('FINISHED REGEX TEST')

    if args.comparison_sfdb:
        logging.info('STARTING COMPARISON TEST')
        sfdb_old = SFDBContainer.from_file(args.comparison_sfdb)
        diverging_lines = sc.check_sfdb_comparison(sfdb_new, sfdb_old, args.ex_lines1, args.ex_lines2, args.ex_col)
        sc.log_sfdb_comparison(diverging_lines)
        warning_counter += len(diverging_lines)
        logging.info('FINISHED COMPARISON TEST')

    if args.write:
        no_dupl_sfdb_file = args.SFDBFile[:-5] + '_no_duplicates.sfdb'
        logging.info('Writing SFDB file without duplicates to {no_dupl_sfdb_file}')
        sfdb_new.write(no_dupl_sfdb_file, sort=args.sorted, remove_duplicates=True)

    # Finish logging
    logging.info('Done')
    print(f'The file caused {warning_counter} warning-messages.')
    print(f'Logfile written to {log_filepath}.\nDone')


if __name__ == '__main__':
    run()
