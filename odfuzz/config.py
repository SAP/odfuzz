"""This module contains classes for fetching and parsing basic configurations."""

import os

from odfuzz.constants import (
    DEFAULT_DATA_FORMAT,
    DEFAULT_USE_ENCODER,
    DEFAULT_SAP_CLIENT,
    DEFAULT_IGNORE_METADATA_RESTRICTIONS,
    DEFAULT_SAP_VENDOR_ENABLED,
    ENV_DATA_FORMAT,
    ENV_USE_ENCODER,
    ENV_SAP_CLIENT,
    ENV_IGNORE_METADATA_RESTRICTIONS,
    ENV_SAP_VENDOR_ENABLED,
)


class FuzzerConfig:
    def __init__(self):
        self._sap_client = os.getenv(ENV_SAP_CLIENT, DEFAULT_SAP_CLIENT)
        self._data_format = os.getenv(ENV_DATA_FORMAT, DEFAULT_DATA_FORMAT)
        self._ignore_restriction = os.getenv(ENV_IGNORE_METADATA_RESTRICTIONS,DEFAULT_IGNORE_METADATA_RESTRICTIONS)
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
    def ignore_restriction(self):
        return self._ignore_restriction

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

class Config:
    fuzzer = None

    @staticmethod
    def init():
        Config.fuzzer = FuzzerConfig()
