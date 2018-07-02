"""This module contains functions for initializing loggers"""

import os
import string
import logging.config

from odfuzz.constants import FUZZER_LOGGER, STATS_LOGGER, FILTER_LOGGER, CONFIG_PATH

NONE_TYPE_POSSIBLE = 'n'


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
