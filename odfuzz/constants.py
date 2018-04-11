"""This module contains global constants."""

LOGGER_NAME = 'odfuzz'
MONGODB_NAME = 'fuzzer'

CLIENT = 'sap-client=500'
FORMAT = '$format=json'

ENV_USERNAME = 'SAP_USERNAME'
ENV_PASSWORD = 'SAP_PASSWORD'

EXCLUDE = 'Exclude'
INCLUDE = 'Include'
SEARCH = 'SEARCH'
TOP = 'TOP'
SKIP = 'SKIP'
FILTER = 'FILTER'
GLOBAL_ENTITY = '$E_ALL$'

QUERY_OPTIONS = [FILTER, SEARCH, TOP, SKIP]

SEED_POPULATION = 20
