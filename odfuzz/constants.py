"""This module contains global constants."""

FUZZER_LOGGER = 'odfuzz'
STATS_LOGGER = 'stats'
FILTER_LOGGER = 'filter'
CONFIG_PATH = 'config/logging/logging.conf'

MONGODB_NAME = 'odfuzz'
MONGODB_COLLECTION = 'entities'

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

QUERY_OPTIONS = [FILTER, ORDERBY, TOP, SKIP]

STRING_FUNC_PROB = 0.70
MATH_FUNC_PROB = 0.15
DATE_FUNC_PROB = 0.15
FUNCTION_WEIGHT = 0.3
SINGLE_VALUE_PROB = 0.2

LOGICAL_OPERATORS = {'and': 0.5, 'or': 0.5}
BOOLEAN_OPERATORS = {'eq': 0.5, 'ne': 0.5}
EXPRESSION_OPERATORS = {'eq': 0.3, 'ne': 0.3, 'gt': 0.1, 'ge': 0.1, 'lt': 0.1, 'le': 0.1}

FILTER_PROBABILITY = 0.8
SEED_POPULATION = 5
RECURSION_LIMIT = 3
POOL_SIZE = 10
STRING_THRESHOLD = 200
ITERATIONS_THRESHOLD = 30
SCORE_THRESHOLD = 1000
CONTENT_LEN_SIZE = 50000
INT_MAX = 2147483646

PARTS_NUM = 2
SCORE_EPS = 200
ELITE_PROB = 0.7
FILTER_DEL_PROB = 0.3
ORDERBY_DEL_PROB = 0.1
OPTION_DEL_PROB = 0.1

TOP_ENTITIES = 20
OVERALL_FILE = 'overall.txt'

# this requirement is used in various SAP applications due to system checks;
# while testing the casual OData service, please leave the string empty as ''
SPECIAL_FILTER_REQUIREMENT = 'IsActiveEntity eq true'
