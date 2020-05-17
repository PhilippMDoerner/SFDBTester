from sfdbtester.sfdb import sfdb_tests as st
import logging
from sfdbtester.sfdb.sfdb import SFDBContainer
from datetime import datetime
from sfdbtester.common.argparser import get_args


def main(args):
	# Get SFDB File Object
	sfdb_new = SFDBContainer.from_file(args.SFDBFile)

	# Initialize logging
	now = f'{datetime.now():%y-%m-%d_%H%M%S}'
	log_file_path = f'{args.SFDBFile[:-5]}_{now}_log.txt'
	LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
	handler = logging.FileHandler(log_file_path, 'w', 'utf-8')
	logging.basicConfig(level=logging.DEBUG,
						format=LOG_FORMAT,
						handlers=[handler])
	logger = logging.getLogger('main')
	logger.info(f'LOG FILE FOR SFDB FILE : {args.SFDBFile}')
	logger.info('Indices in this log start from 1')

	warning_counter = 0

	# Perform Tests on SFDB file
	logger.info('START FORMAT TEST')
	warning_counter += st.test_sfdb_format(sfdb_new)
	logger.info('FORMAT TEST FINISHED')

	logger.info('START DATATYPE TEST')
	warning_counter += st.test_sfdb_datatypes(sfdb_new)
	logger.info('DATATYPE TEST FINISHED')

	if args.re:
		logger.info('START REGEX TEST')
		warning_counter += st.test_sfdb_against_regex(sfdb_new, args.re)
		logger.info("REGEX TEST FINISHED")

	if args.comparison_sfdb:
		logger.info('START COMPARISON TEST')
		sfdb_old = SFDBContainer.from_file(args.comparison_sfdb)
		warning_counter += st.compare_sfdb_files(sfdb_new, sfdb_old,
																args.ex_lines1, args.ex_lines2,
																args.ex_col)
		logger.info('COMPARISON TEST FINISHED')

	if args.write:
		no_dupl_sfdb_file = args.SFDBFile[:-5] + '_no_duplicates.sfdb'
		logger.info('Writing SFDB file without duplicates to {no_dupl_sfdb_file}')
		sfdb_new.write(no_dupl_sfdb_file, sorted=args.sorted)

	# Finish logging
	logger.info('Done')
	print(f'The file caused {warning_counter} warning-messages.')
	print(f'Logfile written to {log_file_path}.\nDone')


if __name__ == '__main__':
	main(get_args())
