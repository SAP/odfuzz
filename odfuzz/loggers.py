"""This module contains functions for initializing loggers"""

import os
import uuid
import errno
import string
import logging.config

from datetime import datetime
from collections import namedtuple

from odfuzz.constants import FUZZER_LOGS_NAME, STATS_LOGS_NAME, FILTER_LOGS_NAME, CONFIG_PATH

NONE_TYPE_POSSIBLE = 'n'

Directories = namedtuple('directories', 'logs stats')


class DirectoriesCreator(object):
    def __init__(self, logs_directory, stats_directory):
        self._logs_directory = logs_directory
        self._stats_directory = stats_directory

    def create(self):
        logs_path = build_directory_path(self._logs_directory)
        make_directory(logs_path)

        if self._logs_directory == self._stats_directory:
            stats_path = logs_path
        else:
            stats_path = build_directory_path(self._stats_directory)
            make_directory(stats_path)

        return Directories(logs_path, stats_path)


class LogFormatter(string.Formatter):
    def format_field(self, value, format_spec):
        if format_spec == NONE_TYPE_POSSIBLE:
            normalized_value = none_to_str(value)
            return normalized_value
        else:
            return super().format_field(value, format_spec)


def none_to_str(value):
    if value is None:
        return ''
    else:
        return str(value)


def init_loggers(logs_directory, stats_directory):
    config_defaults = create_config_defaults(logs_directory, stats_directory)
    logging.config.fileConfig(CONFIG_PATH, disable_existing_loggers=False, defaults=config_defaults)


def create_config_defaults(logs_path, stats_path):
    fuzzer = log_file_path(logs_path, FUZZER_LOGS_NAME, 'txt')
    stats_overall = log_file_path(stats_path, STATS_LOGS_NAME, 'csv')
    stats_filter = log_file_path(stats_path, FILTER_LOGS_NAME, 'csv')
    config_defaults = {'logs_file': fuzzer, 'stats_file': stats_overall,
                       'filter_file': stats_filter}
    return config_defaults


def log_file_path(directory, logger_name, file_type):
    file_name = '{}.{}'.format(logger_name, file_type)
    file_path = os.path.join(directory, file_name)
    return file_path


def build_directory_path(directory):
    if directory is None:
        directory = os.getcwd()

    subdirectory = '{}_{}'.format(datetime.now().strftime('%Y-%m-%dT%H-%M-%S'), str(uuid.uuid1()))
    result_directory = os.path.join(directory, subdirectory)
    if os.name == 'nt':
        result_directory = str(result_directory).replace('\\', '\\\\')
    return result_directory


def make_directory(directory):
    try:
        os.makedirs(directory)
    except OSError as os_ex:
        if os_ex != errno.EEXIST:
            raise RuntimeError('Cannot create directory \'{}\''.format(directory))
