"""This module contains global constants."""

import os

RELATIVE_CONFIG_PATH = 'config/fuzzer/config.yaml'
LOGGING_CONFIG_PATH = 'config/logging/logging.conf'
CERTIFICATE_PATH = 'config/security/ca_sap_root_base64.crt'

FUZZER_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))
FUZZER_CONFIG_PATH = os.path.join(FUZZER_PATH, RELATIVE_CONFIG_PATH)
FUZZER_LOGGING_CONFIG_PATH = os.path.join(FUZZER_PATH, LOGGING_CONFIG_PATH)

FUZZER_LOGS_NAME = 'logs'
STATS_LOGS_NAME = 'stats_overall'
FILTER_LOGS_NAME = 'stats_filter'
DATA_RESPONSES_NAME = 'data_responses'
URLS_LOGS_NAME = 'list_urls'
RUNTIME_FILE_NAME = 'runtime_info.txt'

# this set of constants must be equal to the corresponding
# logger keys defined in the CONFIG_PATH
FUZZER_LOGGER = 'fuzzer'
STATS_LOGGER = 'stats'
FILTER_LOGGER = 'filter'
URLS_LOGGER = 'urls'
RESPONSE_LOGGER = 'data'

MONGODB_NAME = 'odfuzz'
ACCESS_PROTOCOL = 'https://'

ENV_USERNAME = 'SAP_USERNAME'
ENV_PASSWORD = 'SAP_PASSWORD'

EXCLUDE = 'Exclude'
INCLUDE = 'Include'
EXPAND = '$expand'
ORDERBY = '$orderby'
TOP = '$top'
SKIP = '$skip'
FILTER = '$filter'
SEARCH = 'search'
INLINECOUNT = '$inlinecount'

GLOBAL_ENTITY_SET = '$ENTITY_SET$'
GLOBAL_ENTITY = '$ENTITY$'
GLOBAL_ENTITY_ASSOC = '$ENTITY_ASSOC$'
GLOBAL_FUNCTION = '$F_ALL$'
GLOBAL_PROPRTY = '$P_ALL$'
FORBID_OPTION = '$FORBID$'
DRAFT_OBJECTS = '$DRAFT$'
NAV_PROPRTY = '$NAV_PROP$'
VALUE = '$VALUE$'

QUERY_OPTIONS = [FILTER, ORDERBY, TOP, SKIP, EXPAND, SEARCH, INLINECOUNT]
SINGLE_ENTITY_ALLOWED_OPTIONS = [FILTER, EXPAND]

STRING_FUNC_PROB = 0.70
MATH_FUNC_PROB = 0.15
DATE_FUNC_PROB = 0.15
FUNCTION_WEIGHT = 0.3
SINGLE_VALUE_PROB = 0.2
SINGLE_ENTITY_PROB = 0.05
INLINECOUNT_ALL_PAGES_PROB = 0.5

SEARCH_MAX_LEN = 20
FUZZY_SEARCH_WILDCARD_PROB = 0.2
FUZZY_SEARCH_WITHOUT = 0.2
FUZZY_SEARCH_OR_PROB = 0.2
FUZZY_SEARCH_EQUAL_PROB = 0.2
MAX_FUZZY_SEARCH_ORS = 3

LOGICAL_OPERATORS = {'and': 0.5, 'or': 0.5}
BOOLEAN_OPERATORS = {'eq': 0.5, 'ne': 0.5}
INTERVAL_OPERATORS = {'le': 0.5, 'ge': 0.5}
EXPRESSION_OPERATORS = {'eq': 0.3, 'ne': 0.3, 'gt': 0.1, 'ge': 0.1, 'lt': 0.1, 'le': 0.1}
SEARCH_WILDCARDS = ['*', '%']

FILTER_CROSS_PROBABILITY = 0.8
KEY_VALUES_MUTATION_PROB = 0.05
ASSOCIATED_ENTITY_PROB = 0.5
RECURSION_LIMIT = 3

STRING_THRESHOLD = 200
ITERATIONS_THRESHOLD = 30
CONTENT_LEN_SIZE = 50000
INT_MAX = 2147483647

FILTER_PARTS_NUM = 2
ORDERBY_MAX_PROPS = 3

SCORE_EPS = 200
ELITE_PROB = 0.7
FILTER_DEL_PROB = 0.1
ORDERBY_DEL_PROB = 0.1
OPTION_DEL_PROB = 0.1
MAX_MULTI_VALUES = 3
MAX_EXPAND_VALUES = 3
FILTER_SAMPLE_SIZE = 30
MAX_BEST_QUERIES = 30

CSV = 'StatusCode;ErrorCode;ErrorMessage;EntitySet;AccessibleSet;AccessibleKeys;Property;orderby;top;skip;filter;expand;search;inlinecount;hash'
CSV_FILTER = 'StatusCode;ErrorCode;ErrorMessage;EntitySet;Property;logical;operator;function;operand;hash'
CSV_RESPONSES_HEADER = 'Time;Data;EntitySet;URL;Brief'

INFINITY_TIMEOUT = -1
YEAR_IN_SECONDS = 31622400
REQUEST_TIMEOUT = 600
RETRY_TIMEOUT = 100

ASYNC_REQUESTS_NUM = 10
SAP_CLIENT = '500'
DATA_FORMAT = 'json'
URLS_PER_PROPERTY = 100

HEX_BINARY = 'ABCDEFabcdef0123456789'
BASE_CHARSET = 'abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ0123456789~!$@^*()_+-–—=' \
               '[]|:<>.‰¨œƒ…†‡Œ‘’´`“”•™¡¢£¤¥¦§©ª«¬®¯°±²³µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍ' \
               'ÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ{} '

NON_EXISTING_MULTIPLICITY = '-1'
