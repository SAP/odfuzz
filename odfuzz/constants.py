"""This module contains global constants."""
import os
from datetime import datetime

# configuration constants, used while initializing loggers which are used for logging stats and logging info messages;
# used in loggers.py
LOGGING_CONFIG_PATH = 'config/logging/logging.conf'

FUZZER_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))
FUZZER_LOGGING_CONFIG_PATH = os.path.join(FUZZER_PATH, LOGGING_CONFIG_PATH)

FUZZER_LOGS_NAME = 'logs'
STATS_LOGS_NAME = 'stats_overall'
FILTER_LOGS_NAME = 'stats_filter'
DATA_RESPONSES_NAME = 'data_responses'
URLS_LOGS_NAME = 'list_urls'

# this set of constants must be equal to the corresponding
# logger keys defined in the CONFIG_PATH
FUZZER_LOGGER = 'fuzzer'
STATS_LOGGER = 'stats'
FILTER_LOGGER = 'filter'
URLS_LOGGER = 'urls'
RESPONSE_LOGGER = 'data'

# used in databases.py as a name of the database in MongoDB (https://docs.mongodb.com/manual/core/databases-and-collections/);
# collections are created for each OData service separately
MONGODB_NAME = 'odfuzz'

# used for mounting adapters in the module `requests` (this may be located right in Dispatcher)
ACCESS_PROTOCOL = 'https://'
# used in Dispatcher (fuzzer.py) to obtain SAP login from environmental variables
# TODO this should probably be used in one place only (config.py) and not scattered + rename with prefix ODFUZZ_
ENV_USERNAME = 'ODFUZZ_USERNAME'
ENV_PASSWORD = 'ODFUZZ_PASSWORD'
ENV_SAP_CLIENT = 'ODFUZZ_SAP_CLIENT'
ENV_DATA_FORMAT = 'ODFUZZ_DATA_FORMAT'
ENV_URLS_PER_PROPERTY = 'ODFUZZ_URLS_PER_PROPERTY'
ENV_ASYNC_REQUESTS_NUM = 'ODFUZZ_ASYNC_REQUESTS_NUM'
ENV_ODFUZZ_CERTIFICATE_PATH = 'ODFUZZ_CERTIFICATE_PATH'
ENV_USE_ENCODER = 'ODFUZZ_USE_ENCODER'
ENV_IGNORE_METADATA_RESTRICTIONS = 'ODFUZZ_IGNORE_METADATA_RESTRICTIONS'
ENV_CLI_RUNNER_SEED = 'ODFUZZ_CLI_RUNNER_SEED' #ability to set the "random.seed()" in CLI runner for example for debugging or experiments.
ENV_SAP_VENDOR_ENABLED = 'ODFUZZ_SAP_VENDOR_ENABLED'

# default configuration values; these values are retrieved by default if no environment variable overwrites them
DEFAULT_SAP_CLIENT = '500'
DEFAULT_DATA_FORMAT = 'json'
DEFAULT_URLS_PER_PROPERTY = 100
DEFAULT_ASYNC_REQUESTS_NUM = 10
DEFAULT_IGNORE_METADATA_RESTRICTIONS = 'False'
DEFAULT_USE_ENCODER = 'True'
DEFAULT_CLI_RUNNER_SEED = datetime.now() #the default value for random.seed() in CLI runner, as was in fuzzer.py hardcoded
DEFAULT_SAP_VENDOR_ENABLED = 'False'


# names of restrictions which are used for searching for keywords; these constants are also used in the module fuzzer.py
# for creating dictionary which is going to be saved to the database - these constants are truly global, so the user
# can change its names based on different versions of OData protocol (the only known difference is in search -> $search)
EXCLUDE = 'Exclude'
INCLUDE = 'Include'
GLOBAL_ENTITY_SET = '$ENTITY_SET$'
GLOBAL_ENTITY = '$ENTITY$'
GLOBAL_ENTITY_ASSOC = '$ENTITY_ASSOC$'
GLOBAL_FUNCTION = '$F_ALL$'
GLOBAL_PROPRTY = '$P_ALL$'
FORBID_OPTION = '$FORBID$'
DRAFT_OBJECTS = '$DRAFT$'
NAV_PROPRTY = '$NAV_PROP$'
VALUE = '$VALUE$'

EXPAND = '$expand'
ORDERBY = '$orderby'
TOP = '$top'
SKIP = '$skip'
FILTER = '$filter'
SEARCH = 'search'
INLINECOUNT = '$inlinecount'

# used for creating restrictions for all query options; if there is no restriction for the query option,
# then the fields are leaved empty in the structure which is used in entities.py
QUERY_OPTIONS = [FILTER, ORDERBY, TOP, SKIP, EXPAND, SEARCH, INLINECOUNT]
SINGLE_ENTITY_ALLOWED_OPTIONS = [FILTER, EXPAND]


# probabilities prepared for selecting the type of function in the $filter query option (entities.py);
# those functions are initialized by Builder (FilterQuery)
STRING_FUNC_PROB = 0.70
MATH_FUNC_PROB = 0.15
DATE_FUNC_PROB = 0.15
FUNCTION_WEIGHT = 0.3
SINGLE_VALUE_PROB = 0.2
SINGLE_ENTITY_PROB = 0.05
RECURSION_LIMIT = 3 #FilterQuery - how long filter query will be generated

# probabilities for generating operators in the $filter query option (FilterQuery - entities.py)
LOGICAL_OPERATORS = {'and': 0.5, 'or': 0.5}
BOOLEAN_OPERATORS = {'eq': 0.5, 'ne': 0.5}
INTERVAL_OPERATORS = {'le': 0.5, 'ge': 0.5}
EXPRESSION_OPERATORS = {'eq': 0.3, 'ne': 0.3, 'gt': 0.1, 'ge': 0.1, 'lt': 0.1, 'le': 0.1}
SEARCH_MAX_LEN = 20

# allowed wildcards that are used in SAP applications; there may exist even more wildcards in OData v4
SEARCH_WILDCARDS = ['*', '%']
# used only in SearchQuery (entities.py)
FUZZY_SEARCH_WILDCARD_PROB = 0.2
FUZZY_SEARCH_WITHOUT = 0.2
FUZZY_SEARCH_OR_PROB = 0.2
FUZZY_SEARCH_EQUAL_PROB = 0.2
MAX_FUZZY_SEARCH_ORS = 3

FILTER_CROSS_PROBABILITY = 0.8
KEY_VALUES_MUTATION_PROB = 0.05
ASSOCIATED_ENTITY_PROB = 0.5

# the constants are used only in Analyzer, or FitnessEvaluator respectively; the values came from the personal
# observations
STRING_THRESHOLD = 200
ITERATIONS_THRESHOLD = 30
CONTENT_LEN_SIZE = 50000

FILTER_PARTS_NUM = 2
ORDERBY_MAX_PROPS = 3

INT_MAX = 2147483647

SCORE_EPS = 200
ELITE_PROB = 0.7
FILTER_DEL_PROB = 0.1
ORDERBY_DEL_PROB = 0.1
OPTION_DEL_PROB = 0.1
MAX_MULTI_VALUES = 3
MAX_EXPAND_VALUES = 3
FILTER_SAMPLE_SIZE = 30
MAX_BEST_QUERIES = 30
INLINECOUNT_ALL_PAGES_PROB = 0.5

# headers for CSV files (StatsLogger, ResponseTimeLogger)
CSV = 'StatusCode;ErrorCode;ErrorMessage;EntitySet;AccessibleSet;AccessibleKeys;Property;orderby;top;skip;filter;expand;search;inlinecount;hash'
CSV_FILTER = 'StatusCode;ErrorCode;ErrorMessage;EntitySet;Property;logical;operator;function;operand;hash'
CSV_RESPONSES_HEADER = 'Time;Data;EntitySet;URL;Brief'

INFINITY_TIMEOUT = -1
YEAR_IN_SECONDS = 31622400
REQUEST_TIMEOUT = 600
RETRY_TIMEOUT = 100

# range for basic charsets for generator (generators.py)
HEX_BINARY = 'ABCDEFabcdef0123456789'

# The character "~" has been  removed from BASE_CHARSET, as since Python 3.7, urllib.parse.quote() uses RFC 3986 for encoding.
# According to this standard "~" is a reserved character and should not be encoded. But upto Python 3.6 this character gets encoded.
# This creates conflicting test results between Python 3.6 and 3.7(and above). 
# TODO: Add back "~" in BASE_CHARSET. In utils.py replace urllib.parse.quote() with something consistent, or remove Python 3.6 support.

BASE_CHARSET = 'abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ0123456789!$@^*()_+-–—=' \
               '[]|:<>.‰¨œƒ…†‡Œ‘’´`“”•™¡¢£¤¥¦§©ª«¬®¯°±²³µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍ' \
               'ÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ{} '

NON_EXISTING_MULTIPLICITY = '-1'

# namespaces required for parsing error messages from responses (this was tested on within SAP applications) (fuzzer.py)
NAMESPACES = {
    'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices',
    'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata',
    'sap': 'http://www.sap.com/Protocols/SAPData',
    'edmx': 'http://schemas.microsoft.com/ado/2007/06/edmx',
    'edm': 'http://schemas.microsoft.com/ado/2008/09/edm',
    'atom': 'http://www.w3.org/2005/Atom'
}
