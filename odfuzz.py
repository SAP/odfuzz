"""The main module for running the ODfuzz fuzzer"""

import sys

from odfuzz.arguments import ArgPaser, ArgParserError


def main():
    arg_parser = ArgPaser()
    try:
        arguments = arg_parser.parse()
    except ArgParserError:
        sys.exit(1)


if __name__ == '__main__':
    main()
