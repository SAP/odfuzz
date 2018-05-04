"""This module contains functions for initializing loggers"""

import os
import sys
import uuid
import errno
import logging.config

from datetime import datetime

from odfuzz.constants import FUZZER_LOGGER, STATS_LOGGER, FILTER_LOGGER, CONFIG_PATH
from odfuzz.exceptions import LoggersError


def init_loggers(logs_directory, stats_directory):
    logs_path = directory_path(logs_directory)
    stats_path = directory_path(stats_directory)
    create_directory(logs_path)
    create_directory(stats_path)

    config_defaults = create_config_defaults(logs_path, stats_path)
    logging.config.fileConfig(CONFIG_PATH, disable_existing_loggers=False, defaults=config_defaults)


def directory_path(directory):
    if directory is None:
        directory = os.getcwd()

    subdirectory = '{}_{}'.format(datetime.now().strftime('%Y-%m-%dT%H-%M-%S'), str(uuid.uuid1()))
    result_directory = os.path.join(directory, subdirectory)
    if os.name == 'nt':
        result_directory = str(result_directory).replace('\\', '\\\\')
    return result_directory


def create_directory(directory):
    try:
        os.makedirs(directory)
    except OSError as os_ex:
        if os_ex != errno.EEXIST:
            raise LoggersError('Cannot create directory \'{}\''.format(directory))


def create_config_defaults(logs_path, stats_path):
    fuzzer = log_file_path(logs_path, FUZZER_LOGGER, 'txt')
    stats_overall = log_file_path(stats_path, STATS_LOGGER, 'csv')
    stats_filter = log_file_path(stats_path, FILTER_LOGGER, 'csv')
    config_defaults = {'logs_file': fuzzer, 'stats_file': stats_overall,
                       'filter_file': stats_filter}
    return config_defaults


def log_file_path(directory, logger_name, file_type):
    file_name = 'odata_{}.{}'.format(logger_name, file_type)
    file_path = os.path.join(directory, file_name)
    return file_path
