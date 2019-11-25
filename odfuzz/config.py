"""This module contains classes for fetching and parsing basic configurations."""

import os

from odfuzz.constants import ENV_ODFUZZ_CERTIFICATE_PATH, DEFAULT_ASYNC_REQUESTS_NUM, DEFAULT_SAP_CLIENT, DEFAULT_DATA_FORMAT, DEFAULT_URLS_PER_PROPERTY, ENV_SAP_CLIENT, ENV_DATA_FORMAT, ENV_URLS_PER_PROPERTY, ENV_ASYNC_REQUESTS_NUM

#TODO: This is in the state of working, but is there any real need for distinguishing Fuzzer and Dispatecher config? even in fuzzer is part of dispatching (url part)
class FuzzerConfig:
    def __init__(self):
        self._sap_client = os.getenv(ENV_SAP_CLIENT, DEFAULT_SAP_CLIENT)
        self._data_format = os.getenv(ENV_DATA_FORMAT, DEFAULT_DATA_FORMAT)
        self._urls_per_property = os.getenv(ENV_URLS_PER_PROPERTY, DEFAULT_URLS_PER_PROPERTY)

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
    def __init__(self):
        self._cert_file_path = self._data_format = os.getenv(ENV_ODFUZZ_CERTIFICATE_PATH) #intentionaly no default path
        self._data_format = os.getenv(ENV_DATA_FORMAT, DEFAULT_DATA_FORMAT)
        self._async_requests_num = os.getenv(ENV_ASYNC_REQUESTS_NUM, DEFAULT_ASYNC_REQUESTS_NUM)

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
    @staticmethod
    def init():
        Config.fuzzer = FuzzerConfig()
        Config.dispatcher = DispatcherConfig()