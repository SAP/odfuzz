"""This module contains a wrapper for parsing command line arguments."""

import sys
import argparse

from odfuzz.constants import INFINITY_TIMEOUT, YEAR_IN_SECONDS, FUZZER_CONFIG_PATH
from odfuzz.exceptions import ArgParserError

FUZZER_DESC = 'Fuzzer for testing applications communicating via the OData protocol'


class ArgParser:
    def __init__(self):
        self._parser = argparse.ArgumentParser(prog='ODfuzz', add_help=False, description=FUZZER_DESC)
        self._add_arguments()
        self._set_defaults()

    def parse(self, arguments):
        self._handle_help_option(arguments)
        try:
            parsed_arguments = self._parser.parse_args(arguments)
        except SystemExit:
            raise ArgParserError('Cannot parse command line arguments')
        if parsed_arguments.timeout >= YEAR_IN_SECONDS:
            raise ArgParserError('Fuzzer cannot run for over a year')
        return parsed_arguments

    def _add_arguments(self):
        self._parser.add_argument('service', type=str, help='An OData service URL')
        self._parser.add_argument('-l', '--logs', type=str, help='A logs directory')
        self._parser.add_argument('-s', '--stats', type=str, help='A statistics directory')
        self._parser.add_argument('-r', '--restrictions', type=str, help='A user defined restrictions')
        self._parser.add_argument('-t', '--timeout', type=int, default=INFINITY_TIMEOUT,
                                  help='A general timeout in seconds for a fuzzing')
        self._parser.add_argument('-a', '--asynchronous', action='store_true', default=False,
                                  help='Allow ODfuzz to send HTTP requests asynchronously')
        self._parser.add_argument('-f', '--first-touch', action='store_true', default=False,
                                  help='Automatically determine which entities are queryable')
        self._parser.add_argument('-p', '--plot', action='store_true', default=False,
                                  help='Log response time and data, and create a scatter plot')
        self._parser.add_argument('-c', '--credentials', type=str, metavar='USERNAME:PASSWORD',
                                  help='User name and password used for authentication')
        self._parser.add_argument('--fuzzer-config', type=str, help='A configuration file for the fuzzer')

    def _set_defaults(self):
        self._parser.set_defaults(fuzzer_config=FUZZER_CONFIG_PATH)

    def _handle_help_option(self, arguments):
        if '-h' in arguments or '--help' in arguments:
            self._parser.print_help()
            sys.exit(0)
