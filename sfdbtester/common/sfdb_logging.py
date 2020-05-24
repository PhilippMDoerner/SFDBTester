import logging
from logging import config
from datetime import datetime
from sfdbtester.common.utilities import get_resource_filepath

LOGFILE_LEVEL = 15


def configurate_logger(log_filepath):
    logging.addLevelName(LOGFILE_LEVEL, 'LOGFILE')
    logging.log_filepath = log_filepath

    config_file = get_resource_filepath('logging.cfg')
    logging.config.fileConfig(config_file)


def create_log_filepath(sfdb_filepath):
    sfdb_filepath = 'fileless.sfdb' if sfdb_filepath == '' else sfdb_filepath
    now = f'{datetime.now():%y-%m-%d_%H%M%S}'

    log_filepath = f'{sfdb_filepath[:-5]}_{now}.log'

    return log_filepath
