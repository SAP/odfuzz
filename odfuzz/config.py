"""This module contains classes for fetching and parsing basic configurations."""

import yaml

from odfuzz.constants import FUZZER_CONFIG_PATH, CONFIG_SECTION, CERTIFICATE_PATH, ASYNC_REQUESTS_NUM,\
    SAP_CLIENT, DATA_FORMAT, URLS_PER_PROPERTY
from odfuzz.exceptions import ConfigParserError


class ConfigParser:

    @staticmethod
    def parse(config_file):
        try:
            with open(config_file) as stream:
                config_dict = yaml.safe_load(stream)
        except (EnvironmentError, yaml.YAMLError) as error:
            raise ConfigParserError('An exception was raised while parsing the restrictions file \'{}\': {}'
                                    .format(config_file, error))

        return Config(config_dict)


class Config:
    def __init__(self, config):
        self._fuzzer = FuzzerConfig(config['fuzzer'])
        self._dispatcher = DispatcherConfig(config['dispatcher'])

    @property
    def fuzzer(self):
        return self._fuzzer

    @property
    def dispatcher(self):
        return self._dispatcher


class FuzzerConfig:
    def __init__(self, config):
        self._sap_client = config.get('sap_client', SAP_CLIENT)
        self._data_format = config.get('data_format', DATA_FORMAT)
        self._urls_per_property = config.get(
            'urls_per_property', URLS_PER_PROPERTY)

    @property
    def sap_client(self):
        return self._sap_client

    @property
    def data_format(self):
        return self._data_format

    @property
    def urls_per_property(self):
        return self._urls_per_property


class DispatcherConfig:
    def __init__(self, config):
        self._cert_install_path = config.get('cert_install_path', True)
        self._cert_file_path = config.get('cert_file_path', CERTIFICATE_PATH)
        self._async_requests_num = config.get(
            'async_requests_num', ASYNC_REQUESTS_NUM)

    @property
    def cert_install_path(self):
        return self._cert_install_path

    @property
    def cert_file_path(self):
        return self._cert_file_path

    @property
    def async_requests_num(self):
        return self._async_requests_num
