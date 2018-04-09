from odfuzz.exceptions import RestrictionsError

EXCLUDE = 'Exclude'
INCLUDE = 'Include'
SEARCH = 'SEARCH'
TOP = 'TOP'
SKIP = 'SKIP'
FILTER = 'FILTER'


class RestrictionsGroup(object):
    def __init__(self, restrictions_file):
        self._restrictions_file = restrictions_file
        self._restrictions = None
        self._include = None
        self._exclude = None
        self._parse_restrictions()

    @property
    def include(self):
        return self._include

    @property
    def exclude(self):
        return self._exclude

    def _parse_restrictions(self):
        try:
            restrictions_lines = read_lines(self._restrictions_file)
        except EnvironmentError as env_error:
            raise RestrictionsError('An exception was raised while reading a file: {}'
                                    .format(env_error))
        try:
            restrictions_dict = convert_to_dict(restrictions_lines)
        except TypeError as typ_error:
            raise RestrictionsError('An exception was raised during a dictionary conversion: {}'
                                    .format(typ_error))
        self._init_restrictions(restrictions_dict)

    def _init_restrictions(self, restrictions_dict):
        self._exclude = Restriction(restrictions_dict.get(EXCLUDE, None))
        self._include = Restriction(restrictions_dict.get(EXCLUDE, None))


class Restriction(object):
    def __init__(self, restriction):
        self._restriction = restriction
        self._filter = None
        self._skip = None
        self._top = None
        self._search = None

        if restriction:
            self._init_restriction()

    @property
    def filter(self):
        return self._filter

    @property
    def skip(self):
        return self._skip

    @property
    def top(self):
        return self._top

    @property
    def search(self):
        return self._search

    def _init_restriction(self):
        self._init_query_restrictions('_filter', FILTER)
        self._init_query_restrictions('_skip', SKIP)
        self._init_query_restrictions('_top', TOP)
        self._init_query_restrictions('_search', SEARCH)

    def _init_query_restrictions(self, property_name, query_name):
        query_restrictions = self._restriction.get(query_name, None)
        if query_restrictions:
            for key, restricted_item in query_restrictions.items():
                setattr(self, property_name, restricted_item)


def read_lines(file_path):
    with open(file_path) as file_object:
        return file_object.read().split('\n')


def convert_to_dict(lines):
    dictionary = {}
    entity_dict = None
    query_dict = None
    restr_dict = None

    for line in lines:
        if line[:3] == '\t\t\t':
            entity_dict.append(line[3:])
        elif line[:2] == '\t\t':
            entity_dict = query_dict[line[2:]] = []
        elif line[:1] == '\t':
            query_dict = restr_dict[line[1:]] = {}
        else:
            restr_dict = dictionary[line] = {}

    return dictionary
