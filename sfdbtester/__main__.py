import logging
from datetime import datetime
from sfdbtester.common.argparser import get_args
from sfdbtester.sfdb.sfdb import SFDBContainer
from sfdbtester.sfdb import sfdb_tests as st


def create_main_logger(log_filepath):
	LOG_FORMAT = "%(levelname)s - %(message)s"
	handler = logging.FileHandler(log_filepath, 'w', 'utf-8')
	logging.basicConfig(level=logging.DEBUG,
						format=LOG_FORMAT,
						handlers=[handler])
	return logging.getLogger('main')


def main(args):
	# Initialize logging
	now = f'{datetime.now():%y-%m-%d_%H%M%S}'
	log_filepath = f'{args.SFDBFile[:-5]}_{now}_log.txt'
	logger = create_main_logger(log_filepath)
	logger.info(f'LOG FILE FOR SFDB FILE : {args.SFDBFile}')
	logger.info('Indices in this log start from 1')

	warning_counter = 0

	# Get SFDB File Object
	sfdb_new = SFDBContainer.from_file(args.SFDBFile)

	# Perform Tests on SFDB file
	warning_counter += st.test_sfdb_format(sfdb_new)

	logger.info('START DATATYPE TEST')
	warning_counter += st.test_sfdb_datatypes(sfdb_new)
	logger.info('FINISHED  DATATYPE TEST')

	if args.re:
		logger.info('START REGEX TEST')
		warning_counter += st.test_sfdb_against_regex(sfdb_new, args.re)
		logger.info("FINISHED  REGEX TEST")

	if args.comparison_sfdb:
		logger.info('START COMPARISON TEST')
		sfdb_old = SFDBContainer.from_file(args.comparison_sfdb)
		warning_counter += st.compare_sfdb_files(sfdb_new, sfdb_old, args.ex_lines1, args.ex_lines2, args.ex_col)
		logger.info('FINISHED COMPARISON TEST')

	if args.write:
		no_dupl_sfdb_file = args.SFDBFile[:-5] + '_no_duplicates.sfdb'
		logger.info('Writing SFDB file without duplicates to {no_dupl_sfdb_file}')
		sfdb_new.write(no_dupl_sfdb_file, sort=args.sorted)

	# Finish logging
	logger.info('Done')
	print(f'The file caused {warning_counter} warning-messages.')
	print(f'Logfile written to {log_filepath}.\nDone')


if __name__ == '__main__':
	main(get_args())
