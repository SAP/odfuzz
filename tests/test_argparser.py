import pytest

from odfuzz.arguments import ArgParserError


def test_argument_parsing(argparser):
    parsed_arguments = argparser.parse(
        ['https://www.odata.org/', '-s', 'stats', '-l', 'logs', '-a', '-r', 'restrict'])

    assert parsed_arguments.service == 'https://www.odata.org/'
    assert parsed_arguments.stats == 'stats'
    assert parsed_arguments.logs == 'logs'
    assert parsed_arguments.restr == 'restrict'
    assert parsed_arguments.async


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
