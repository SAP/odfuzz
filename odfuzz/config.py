"""This module contains classes for fetching and parsing basic configurations."""

import os

from odfuzz.constants import (
    DEFAULT_ASYNC_REQUESTS_NUM,
    DEFAULT_DATA_FORMAT,
    DEFAULT_USE_ENCODER,
    DEFAULT_SAP_CLIENT,
    DEFAULT_URLS_PER_PROPERTY,
    DEFAULT_IGNORE_METADATA_RESTRICTIONS,
    DEFAULT_CLI_RUNNER_SEED,
    DEFAULT_SAP_VENDOR_ENABLED,
    ENV_ASYNC_REQUESTS_NUM,
    ENV_DATA_FORMAT,
    ENV_USE_ENCODER,
    ENV_ODFUZZ_CERTIFICATE_PATH,
    ENV_SAP_CLIENT,
    ENV_URLS_PER_PROPERTY,
    ENV_IGNORE_METADATA_RESTRICTIONS,
    ENV_CLI_RUNNER_SEED,
    ENV_SAP_VENDOR_ENABLED,
)


class FuzzerConfig:
    def __init__(self):
        self._sap_client = os.getenv(ENV_SAP_CLIENT, DEFAULT_SAP_CLIENT)
        self._data_format = os.getenv(ENV_DATA_FORMAT, DEFAULT_DATA_FORMAT)
        env_url_per_property =  os.getenv(ENV_URLS_PER_PROPERTY, DEFAULT_URLS_PER_PROPERTY)
        self._urls_per_property = int(env_url_per_property)
        self._ignore_restriction = os.getenv(ENV_IGNORE_METADATA_RESTRICTIONS,DEFAULT_IGNORE_METADATA_RESTRICTIONS)
        self._cli_runner_seed = os.getenv(ENV_CLI_RUNNER_SEED, DEFAULT_CLI_RUNNER_SEED)
        self._http_method_enabled = "GET"
        self._sap_vendor_enabled = True if os.getenv(ENV_SAP_VENDOR_ENABLED, DEFAULT_SAP_VENDOR_ENABLED) == 'True' else False

        if os.getenv(ENV_USE_ENCODER, DEFAULT_USE_ENCODER) == 'True':
            self._use_encoder = True
        else:
            self._use_encoder = False

    @property
    def use_encoder(self):
        return self._use_encoder

    @property
    def sap_client(self):
        return self._sap_client

    @property
    def data_format(self):
        return self._data_format

    @property
    def urls_per_property(self):
        return self._urls_per_property

    @property
    def ignore_restriction(self):
        return self._ignore_restriction

    @property
    def cli_runner_seed(self):
        return self._cli_runner_seed

    @property
    def http_method_enabled(self):
        return self._http_method_enabled

    @http_method_enabled.setter
    def http_method_enabled(self, value):
        self._http_method_enabled = value
    
    @property
    def sap_vendor_enabled(self):
        return self._sap_vendor_enabled
    
    @sap_vendor_enabled.setter
    def sap_vendor_enabled(self, value):
        self._sap_vendor_enabled = value

class DispatcherConfig:
    def __init__(self):
        self._cert_file_path = self._data_format = os.getenv(ENV_ODFUZZ_CERTIFICATE_PATH) #intentionaly no default path
        self._data_format = os.getenv(ENV_DATA_FORMAT, DEFAULT_DATA_FORMAT)
        async_requests_num =   os.getenv(ENV_ASYNC_REQUESTS_NUM, DEFAULT_ASYNC_REQUESTS_NUM)
        self._async_requests_num = int(async_requests_num)


    @property
    def has_certificate(self):
        return bool(self._cert_file_path)


    @property
    def cert_file_path(self):
        return self._cert_file_path

    @property
    def async_requests_num(self):
        return self._async_requests_num


class Config:
    fuzzer = None
    dispatcher = None

    @staticmethod
    def init():
        Config.fuzzer = FuzzerConfig()
        Config.dispatcher = DispatcherConfig()
