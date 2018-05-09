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

from odfuzz.arguments import ArgPaser
from odfuzz.fuzzer import Manager
from odfuzz.statistics import Stats, StatsPrinter
from odfuzz.loggers import init_loggers
from odfuzz.exceptions import ArgParserError, ODfuzzException


def main():
    gevent.signal(signal.SIGINT, signal_handler)

    arg_parser = ArgPaser()
    try:
        arguments = arg_parser.parse()
    except ArgParserError:
        sys.exit(1)

    directories = create_directories(arguments.logs, arguments.stats)
    init_basic_stats(directories.stats)
    init_loggers(directories.logs, directories.stats)

    manager = Manager(arguments)
    try:
        manager.start()
    except ODfuzzException as fuzzer_ex:
        sys.stderr.write(str(fuzzer_ex))
        sys.exit(1)


def create_directories(logs_directory, stats_directory):
    logs_path = directory_path(logs_directory)
    stats_path = directory_path(stats_directory)
    make_directory(logs_path)
    make_directory(stats_path)

    directories = namedtuple('directories', 'logs stats')
    return directories(logs_path, stats_path)


def directory_path(directory):
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
