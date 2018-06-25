import pytest

from odfuzz.arguments import ArgParser, ArgParserError


def test_argument_parsing():
    argparser = ArgParser()

    parsed_arguments = argparser.parse(
        ['https://www.odata.org/', '-s', 'stats', '-l', 'logs', '-a', '-r', 'restrict'])

    assert parsed_arguments.service == 'https://www.odata.org/'
    assert parsed_arguments.stats == 'stats'
    assert parsed_arguments.logs == 'logs'
    assert parsed_arguments.restr == 'restrict'
    assert parsed_arguments.async


def test_missing_url():
    argparser = ArgParser()

    with pytest.raises(ArgParserError):
        argparser.parse(['-s', 'stats', '-l', 'logs'])


def test_missing_log_directory():
    argparser = ArgParser()

    with pytest.raises(ArgParserError):
        argparser.parse(['https://www.odata.org/', '-s', 'stats', '-l'])


def test_missing_stats_directory():
    argparser = ArgParser()

    with pytest.raises(ArgParserError):
        argparser.parse(['https://www.odata.org/', '-l', 'logs', '-s'])


def test_unrecognized_arguments():
    argparser = ArgParser()

    with pytest.raises(ArgParserError):
        argparser.parse(['https://www.odata.org/', 'WRONG_ARGUMENT'])
    with pytest.raises(ArgParserError):
        argparser.parse(['https://www.odata.org/', '-s', 'stats', '-l', 'logs', 'WRONG_ARGUMENT'])
    with pytest.raises(ArgParserError):
        argparser.parse(['https://www.odata.org/', '-a', '-r', 'restrict', '-WRONG_ARGUMENT'])

