import pytest

from odfuzz.constants import INFINITY_TIMEOUT
from odfuzz.arguments import ArgParserError


def test_argument_parsing(argparser):
    parsed_arguments = argparser.parse(
        ['https://www.odata.org/', '-s', 'stats', '-l', 'logs', '-a', '-r', 'restrict', '-t', '1000',
         '-c', 'Username:Password', '-f'])

    assert parsed_arguments.service == 'https://www.odata.org/'
    assert parsed_arguments.stats == 'stats'
    assert parsed_arguments.logs == 'logs'
    assert parsed_arguments.restrictions == 'restrict'
    assert parsed_arguments.credentials == 'Username:Password'
    assert parsed_arguments.timeout == 1000
    assert parsed_arguments.asynchronous
    assert parsed_arguments.first_touch


def test_default_timeout_value(argparser):
    parsed_arguments = argparser.parse(['https://www.odata.org'])
    assert parsed_arguments.timeout == INFINITY_TIMEOUT


def test_inappropriate_timeout_value(argparser):
    with pytest.raises(ArgParserError):
        argparser.parse(['https://www.odata.org', '-t', '100000000000000000000000'])


def test_missing_url(argparser):
    with pytest.raises(ArgParserError):
        argparser.parse(['-s', 'stats', '-l', 'logs'])


def test_missing_log_directory(argparser):
    with pytest.raises(ArgParserError):
        argparser.parse(['https://www.odata.org/', '-s', 'stats', '-l'])


def test_missing_stats_directory(argparser):
    with pytest.raises(ArgParserError):
        argparser.parse(['https://www.odata.org/', '-l', 'logs', '-s'])


def test_only_wrong_argument(argparser):
    with pytest.raises(ArgParserError):
        argparser.parse(['https://www.odata.org/', 'WRONG_ARGUMENT'])


def test_wrong_argument_with_valid_arguments(argparser):
    with pytest.raises(ArgParserError):
        argparser.parse(['https://www.odata.org/', '-s', 'stats', '-l', 'logs', 'WRONG_ARGUMENT'])


def test_wrong_option_with_valid_arguments(argparser):
    with pytest.raises(ArgParserError):
        argparser.parse(['https://www.odata.org/', '-a', '-r', 'restrict', '-WRONG_ARGUMENT'])


def test_help_with_other_arguments(argparser):
    with pytest.raises(SystemExit):
        argparser.parse(['https://www.odata.org', '-a', '-r', 'restrict', '-h'])


def test_help_only_argument(argparser):
    with pytest.raises(SystemExit):
        argparser.parse(['--help'])
