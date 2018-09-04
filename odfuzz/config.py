import configparser

from odfuzz.constants import FUZZER_CONFIG_PATH, CONFIG_SECTION
from odfuzz.exceptions import ConfigParserError


class Config(object):
    client = '500'
    format = 'json'
    seed_size = 100
    # pool size may be limited on some OData services
    # and should be a factor of seed population size
    pool_size = 10

    @staticmethod
    def retrieve_config():
        config = ConfigParser(FUZZER_CONFIG_PATH).get_section(CONFIG_SECTION)
        Config.client = config.client
        Config.format = config.format
        Config.pool_size = config.pool_size
        Config.seed_size = config.seed_size


class ConfigParser(object):
    def __init__(self, config_file):
        self._config_file = config_file
        self._config = configparser.ConfigParser()
        self._read_file()

    def _read_file(self):
        try:
            self._config.read(self._config_file)
        except configparser.Error as error:
            raise ConfigParserError(error)

    def get_section(self, name):
        try:
            parsed_section = self._config[name]
        except KeyError:
            raise ConfigParserError('Section \'{}\' does not exist in file \'{}\''.format(name, self._config_file))
        return SectionConfig(parsed_section)


class SectionConfig(object):
    def __init__(self, parsed_section):
        self._parsed_section = parsed_section

        self._seed_size = None
        self._pool_size = None
        self._client = None
        self._format = None

        self._init_config()

    def _init_config(self):
        self._seed_size = self._parsed_section.getint('seed', 100)
        self._pool_size = self._parsed_section.getint('pool', 10)
        self._client = self._parsed_section.get('client', '500')
        self._format = self._parsed_section.get('format', 'json')

    @property
    def seed_size(self):
        return self._seed_size

    @property
    def pool_size(self):
        return self._pool_size

    @property
    def client(self):
        return self._client

    @property
    def format(self):
        return self._format
