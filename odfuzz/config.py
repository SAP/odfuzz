"""This module contains classes for fetching and parsing basic configurations."""

import yaml
import os

from odfuzz.constants import CERTIFICATE_PATH, ASYNC_REQUESTS_NUM, FUZZER_CONFIG_PATH, \
    SAP_CLIENT, DATA_FORMAT, URLS_PER_PROPERTY, ENV_SAP_CLIENT
from odfuzz.exceptions import ConfigParserError


class FuzzerConfig:
    def __init__(self, config):
        self._sap_client = config.get('sap_client', SAP_CLIENT)
        self._sap_client = os.getenv(ENV_SAP_CLIENT)
        #overwrite if ENV variable exists - https://github.com/SAP/odfuzz/issues/24

        self._data_format = config.get('data_format', DATA_FORMAT)
        self._urls_per_property = config.get('urls_per_property', URLS_PER_PROPERTY)

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
        self._certificate = config.get('certificate')
        if self._certificate:
            self._cert_install_path = self._certificate.get('cert_install_path', True)
            self._cert_file_path = self._certificate.get('cert_file_path', CERTIFICATE_PATH)
        else:
            self._cert_install_path = False
            self._cert_file_path = ''

        self._async_requests_num = config.get('async_requests_num', ASYNC_REQUESTS_NUM)

    @property
    def has_certificate(self):
        if self._certificate:
            return bool(self._cert_file_path)
        return False

    @property
    def cert_install_path(self):
        return self._cert_install_path

    @property
    def cert_file_path(self):
        return self._cert_file_path

    @property
    def async_requests_num(self):
        return self._async_requests_num


class Config:
    fuzzer = FuzzerConfig({})
    dispatcher = DispatcherConfig({})

    @staticmethod
    def init_from(config_file):
        config_dict = Config.raw_from(config_file)
        if not config_dict:
            config_dict = Config.raw_from(FUZZER_CONFIG_PATH)

        Config.fuzzer = FuzzerConfig(config_dict.get('fuzzer') or {})
        Config.dispatcher = DispatcherConfig(config_dict.get('dispatcher') or {})

    @staticmethod
    def raw_from(config_file):
        try:
            with open(config_file) as stream:
                config_dict = yaml.safe_load(stream)
        except (EnvironmentError, yaml.YAMLError) as error:
            raise ConfigParserError('An exception was raised while parsing the configuration file \'{}\': {}'
                                    .format(config_file, error))
        return config_dict
