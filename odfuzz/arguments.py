"""This module contains a wrapper for parsing command line arguments."""

import sys
import argparse

from odfuzz.constants import INFINITY_TIMEOUT, YEAR_IN_SECONDS
from odfuzz.exceptions import ArgParserError

FUZZER_DESC = 'Fuzzer for testing applications communicating via the OData protocol'


class ArgParser(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser(prog='ODfuzz', add_help=False, description=FUZZER_DESC)
        self._add_arguments()

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
        self._parser.add_argument('-r', '--restr', type=str, help='A user defined restrictions')
        self._parser.add_argument('-t', '--timeout', type=int, default=INFINITY_TIMEOUT,
                                  help='A general timeout in seconds for a fuzzing')
        self._parser.add_argument('-a', '--async', action='store_true', default=False,
                                  help='Allow ODfuzz to send HTTP requests asynchronously')
        self._parser.add_argument('-c', '--credentials', type=str, metavar='USERNAME:PASSWORD',
                                  help='User name and password used for authentication')

    def _handle_help_option(self, arguments):
        if '-h' in arguments or '--help' in arguments:
            self._parser.print_help()
            sys.exit(0)
