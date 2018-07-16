"""This module contains global constants."""

FUZZER_LOGS_NAME = 'logs'
STATS_LOGS_NAME = 'stats_overall'
FILTER_LOGS_NAME = 'stats_filter'
RUNTIME_FILE_NAME = 'runtime_info.txt'
CONFIG_PATH = 'config/logging/logging.conf'

# this set of constants must be equal to the corresponding
# logger keys defined in the CONFIG_PATH
FUZZER_LOGGER = 'fuzzer'
STATS_LOGGER = 'stats'
FILTER_LOGGER = 'filter'

MONGODB_NAME = 'odfuzz'

CLIENT = 'sap-client=500'
FORMAT = '$format=json'
ADAPTER = 'https://'

ENV_USERNAME = 'SAP_USERNAME'
ENV_PASSWORD = 'SAP_PASSWORD'

EXCLUDE = 'Exclude'
INCLUDE = 'Include'
ORDERBY = '$orderby'
TOP = '$top'
SKIP = '$skip'
FILTER = '$filter'
GLOBAL_ENTITY = '$E_ALL$'
GLOBAL_FUNCTION = '$F_ALL$'
GLOBAL_PROPRTY = '$P_ALL$'
DRAFT_OBJECTS = '$DRAFT$'

QUERY_OPTIONS = [FILTER, ORDERBY, TOP, SKIP]

STRING_FUNC_PROB = 0.70
MATH_FUNC_PROB = 0.15
DATE_FUNC_PROB = 0.15
FUNCTION_WEIGHT = 0.3
SINGLE_VALUE_PROB = 0.2

LOGICAL_OPERATORS = {'and': 0.5, 'or': 0.5}
BOOLEAN_OPERATORS = {'eq': 0.5, 'ne': 0.5}
EXPRESSION_OPERATORS = {'eq': 0.3, 'ne': 0.3, 'gt': 0.1, 'ge': 0.1, 'lt': 0.1, 'le': 0.1}

FILTER_CROSS_PROBABILITY = 0.8
EMPTY_ENTITY_PROB = 0.001
KEY_VALUES_MUTATION_PROB = 0.05
ASSOCIATED_ENTITY_PROB = 0.2
RECURSION_LIMIT = 3

SEED_POPULATION = 100
# pool size may be limited on some OData services
# and should be a factor of seed population size
POOL_SIZE = 20
STRING_THRESHOLD = 200
ITERATIONS_THRESHOLD = 30
SCORE_THRESHOLD = 1000
CONTENT_LEN_SIZE = 50000
INT_MAX = 2147483646

PARTS_NUM = 2
SCORE_EPS = 200
ELITE_PROB = 0.7
FILTER_DEL_PROB = 0.1
ORDERBY_DEL_PROB = 0.1
OPTION_DEL_PROB = 0.1
TOP_ENTITIES = 20

CSV = 'StatusCode;ErrorCode;ErrorMessage;EntitySet;AccessibleSet;AccessibleKeys;Property;orderby;top;skip;filter'
CSV_FILTER = 'StatusCode;ErrorCode;ErrorMessage;EntitySet;Property;logical;operator;function;operand'
