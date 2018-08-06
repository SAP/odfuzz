"""This module contains a wrapper for parsing command line arguments."""

import sys
from argparse import ArgumentParser

from odfuzz.exceptions import ArgParserError

FUZZER_DESC = 'Fuzzer for testing applications communicating via the OData protocol'


class ArgParser(object):
    def __init__(self):
        self._parser = ArgumentParser(prog='ODfuzz', add_help=False, description=FUZZER_DESC)
        self._add_arguments()

    def parse(self, arguments):
        self._handle_help_option(arguments)
        try:
            parsed_arguments = self._parser.parse_args(arguments)
        except SystemExit:
            raise ArgParserError('Cannot parse command line arguments')
        return parsed_arguments

    def _add_arguments(self):
        self._parser.add_argument('service', type=str, help='An OData service URL')
        self._parser.add_argument('-l', '--logs', type=str, help='A logs directory')
        self._parser.add_argument('-s', '--stats', type=str, help='A statistics directory')
        self._parser.add_argument('-r', '--restr', type=str, help='A user defined restrictions')
        self._parser.add_argument('-a', '--async', action='store_true', default=False,
                                  help='Allow ODfuzz to send HTTP requests asynchronously')

    def _handle_help_option(self, arguments):
        if '-h' in arguments or '--help' in arguments:
            self._parser.print_help()
            sys.exit(0)
