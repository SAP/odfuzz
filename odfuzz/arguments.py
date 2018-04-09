"""This module contains a wrapper for parsing command line arguments"""

from argparse import ArgumentParser

from odfuzz.exceptions import ArgParserError


class ArgPaser(object):
    """An argument parser wrapper"""

    def __init__(self):
        self._parser = ArgumentParser(
            prog='ODfuzz',
            description='Fuzzer for testing applications communicating via the OData protocol'
        )
        self._add_arguments()

    def parse(self):
        """Parse system command line arguments"""
        try:
            return self._parser.parse_args()
        except SystemExit as system_exit:
            raise ArgParserError('An exception was raised while parsing arguments: {}'
                                 .format(system_exit))

    def _add_arguments(self):
        self._parser.add_argument('service', type=str, help='An OData service URL')
        self._parser.add_argument('-l', '--logs', type=str, help='A logs directory')
        self._parser.add_argument('-s', '--stats', type=str, help='A statistics directory')
        self._parser.add_argument('-r', '--restr', type=str, help='A user defined restrictions')
        self._parser.add_argument('-a', '--async', action='store_true', default=False,
                                  help='Allow ODfuzz to send HTTP requests asynchronously')
