# Copyright 2018 SAP SE.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http: //www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

"""The main module for running the ODfuzz fuzzer"""

from gevent import monkey
monkey.patch_all()

import sys
import signal
import logging
import uuid
import os
import errno
import gevent

from collections import namedtuple
from datetime import datetime

from odfuzz.arguments import ArgParser
from odfuzz.fuzzer import Manager
from odfuzz.statistics import Stats, StatsPrinter
from odfuzz.loggers import init_loggers
from odfuzz.exceptions import ArgParserError, ODfuzzException


def main():
    set_signal_handler()

    arg_parser = ArgParser()
    arguments = get_arguments()
    try:
        parsed_arguments = arg_parser.parse(arguments)
    except ArgParserError as argparser_error:
        sys.exit(argparser_error)

    init_logging(parsed_arguments)

    manager = Manager(parsed_arguments)
    try:
        manager.start()
    except ODfuzzException as fuzzer_ex:
        sys.stderr.write(str(fuzzer_ex))
        sys.exit(1)


def set_signal_handler():
    gevent.signal(signal.SIGINT, signal_handler)


def get_arguments():
    command_line_arguments = sys.argv[1:]
    return command_line_arguments


def init_logging(arguments):
    directories = create_directories(arguments.logs, arguments.stats)
    init_basic_stats(directories.stats)
    init_loggers(directories.logs, directories.stats)


def create_directories(logs_directory, stats_directory):
    logs_path = build_directory_path(logs_directory)
    stats_path = build_directory_path(stats_directory)
    make_directory(logs_path)
    make_directory(stats_path)

    directories = namedtuple('directories', 'logs stats')
    return directories(logs_path, stats_path)


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


def init_basic_stats(stats_directory):
    Stats.directory = stats_directory
    Stats.start_datetime = datetime.now()


def signal_handler():
    logging.info('Program interrupted with SIGINT. Exiting...')
    stats = StatsPrinter()
    stats.write()
    sys.exit(0)


if __name__ == '__main__':
    main()
