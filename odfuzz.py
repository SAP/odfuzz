"""The main module for running the ODfuzz fuzzer"""

from gevent import monkey
monkey.patch_all()

import sys
import signal
import logging

from odfuzz.arguments import ArgPaser
from odfuzz.fuzzer import Manager
from odfuzz.exceptions import ArgParserError, ODfuzzException


def main():
    signal.signal(signal.SIGINT, signal_handler)

    arg_parser = ArgPaser()
    try:
        arguments = arg_parser.parse()
    except ArgParserError:
        sys.exit(1)

    manager = Manager(arguments)
    try:
        manager.start()
    except ODfuzzException as fuzzer_ex:
        sys.stderr.write(str(fuzzer_ex))
        sys.exit(1)


def signal_handler(signum, frame):
    signal_name = next(v for v, k in signal.__dict__.items() if k == signum)
    logging.info('Program interrupted with (' + signal_name + ')')
    sys.exit(0)


if __name__ == '__main__':
    main()
