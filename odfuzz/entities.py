"""This module contains a builder class and wrapper classes for queryable entities."""

import copy
import random
import inspect
import uuid

from abc import ABCMeta, abstractmethod
from collections import namedtuple

from pyodata.v2.model import Edmx
from pyodata.exceptions import PyODataException

from odfuzz.exceptions import BuilderError
from odfuzz.generators import RandomGenerator
from odfuzz.monkey import patch_proprties
from odfuzz.constants import CLIENT, GLOBAL_ENTITY, QUERY_OPTIONS, FILTER, SEARCH, TOP, SKIP, \
    STRING_FUNC_PROB, MATH_FUNC_PROB, DATE_FUNC_PROB, GLOBAL_FUNCTION, FUNCTION_WEIGHT, \
    EXPRESSION_OPERATORS, BOOLEAN_OPERATORS, LOGICAL_OPERATORS


class Builder(object):
    """A class for building and initializing all queryable entities."""

    def __init__(self, dispatcher, restrictions):
        self._restrictions = restrictions
        self._dispatcher = dispatcher
        self._queryable = QueryableEntities()

    def build(self):
        data_model = self._get_data_model()
        for entity_set in data_model.entity_sets:
            query_group = QueryGroup(entity_set, self._restrictions)
            self._queryable.add(query_group)
        return self._queryable

    def _get_data_model(self):
        metadata_response = self._get_metadata_from_service()
        try:
            service_model = Edmx.parse(metadata_response.content)
        except PyODataException as pyodata_ex:
            raise BuilderError('An exception occurred while parsing metadata: {}'
                               .format(pyodata_ex))
        return service_model

    def _get_metadata_from_service(self):
        metadata_request = '$metadata?' + CLIENT
        try:
            metadata_response = self._dispatcher.get(metadata_request)
        except Exception as ex:
            raise BuilderError('An exception occurred while retrieving metadata: {}'
                               .format(ex))
        if metadata_response.status_code != 200:
            raise BuilderError('Cannot retrieve metadata from {}. Status code is {}'
                               .format(self._dispatcher.service,
                                       metadata_response.status_code))
        return metadata_response


class QueryableEntities(object):
    """A wrapper that holds a reference to all queryable entities."""

    def __init__(self):
        self._entities = {}

    def add(self, query_group):
        self._entities[query_group.entity_set.name] = query_group

    def get_entity(self, entity_name):
        return self._entities[entity_name]

    def all(self):
        return self._entities.values()


class QueryGroup(object):
    """A group of query options applicable to one entity set."""

    def __init__(self, entity_set, restrictions):
        self._entity_set = entity_set
        self._restrictions = restrictions
        self._query_options = dict.fromkeys(QUERY_OPTIONS)

        self._query_options_list = []
        self._query_filter_required = []
        self._init_group()

    @property
    def entity_set(self):
        return self._entity_set

    def query_options(self):
        return self._query_options.values()

    def query_option(self, query_name):
        return self._query_options[query_name]

    def random_options(self):
        list_length = len(self._query_options_list)
        sample_length = round(random.random() * list_length)
        sample_options = random.sample(self._query_options_list, sample_length)
        return sample_options + self._query_options_list

    def _init_group(self):
        self._init_filter_query()
        self._init_query_type(SEARCH, 'searchable', SearchQuery)
        self._init_query_type(TOP, 'topable', TopQuery)
        self._init_query_type(SKIP, 'pageable', SkipQuery)

    def _init_query_type(self, query_name, metadata_attr, query_object):
        query_restr = self._restrictions.restriction(query_name)
        is_queryable = getattr(self._entity_set, metadata_attr)
        is_not_restricted = self._is_not_restricted(query_restr.exclude)

        if not is_queryable or not is_not_restricted:
            self._query_options[query_name] = query_object(self._entity_set, query_restr)
            self._query_options_list.append(self._query_options[query_name])

    def _init_filter_query(self):
        query_restr = self._restrictions.restriction(FILTER)
        entity_set = self._delete_restricted_proprties(query_restr.exclude)
        is_not_restricted = self._is_not_restricted(query_restr)

        if is_not_restricted and entity_set.entity_type.proprties():
            patch_proprties(entity_set)
            self._query_options[FILTER] = FilterQuery(entity_set, query_restr)
            self._add_filter_option_to_list(entity_set)

    def _add_filter_option_to_list(self, entity_set):
        if entity_set.requires_filter:
            self._query_filter_required.append(self._query_options[FILTER])
        else:
            self._query_options_list.append(self._query_options[FILTER])

    def _is_not_restricted(self, exclude_restr):
        restricted_entities = getattr(exclude_restr, GLOBAL_ENTITY, None)

        if restricted_entities:
            if self._entity_set.name in restricted_entities:
                return False
        return True

    def _delete_restricted_proprties(self, exclude_restr):
        entity_set = copy.deepcopy(self._entity_set)
        restr_proprty_list = exclude_restr.get(self._entity_set.name, [])

        for proprty in self._entity_set.entity_type.proprties():
            if proprty.name in restr_proprty_list or not proprty.filterable:
                del entity_set.entity_type.proprties_dict[proprty.name]

        return entity_set


class QueryOption(metaclass=ABCMeta):
    """An abstract class for a query option."""

    def __init__(self, entity_set, restrictions=None):
        self._entity_set = entity_set
        self._restrictions = restrictions

    @property
    def entity_set(self):
        return self._entity_set

    @property
    def restrictions(self):
        return self._restrictions

    @abstractmethod
    def apply_restrictions(self):
        pass

    @abstractmethod
    def generate(self):
        pass


class SearchQuery(QueryOption):
    """The search query option."""

    def __init__(self, entity, restrictions):
        super(SearchQuery, self).__init__(entity, restrictions)

    def apply_restrictions(self):
        pass

    def generate(self):
        pass


class TopQuery(QueryOption):
    """The $top query option."""

    def __init__(self, entity, restrictions):
        super(TopQuery, self).__init__(entity, restrictions)

    def apply_restrictions(self):
        pass

    def generate(self):
        pass


class SkipQuery(QueryOption):
    """The $skip query option."""

    def __init__(self, entity, restrictions):
        super(SkipQuery, self).__init__(entity, restrictions)

    def apply_restrictions(self):
        pass

    def generate(self):
        pass


class FilterQuery(QueryOption):
    """The $filter query option."""

    def __init__(self, entity, restrictions):
        super(FilterQuery, self).__init__(entity, restrictions)
        self._functions = FilterFunctionsGroup(entity.entity_type.proprties(), restrictions.exclude)
        self._parenthesis_count = 0

    def apply_restrictions(self):
        pass

    def generate(self):
        option = Option()
        option.string += '$filter='
        self._noterm_part(option)
        for _ in range(self._parenthesis_count):
            option.string += ')'
        self._parenthesis_count = 0
        print(option.string)
        return option

    def _noterm_part(self, option):
        option.add_part({})
        self._noterm_type(option)
        self._noterm_comparator(option)
        self._noterm_value(option)
        self._noterm_next(option)

    def _noterm_type(self, option):
        last_part = option.parts[-1]
        last_part['id'] = str(uuid.UUID(int=random.getrandbits(128), version=4))

        if random.random() < 0.5:
            self._parenthesis_count += 1
            option.string += '('
        if random.random() < FUNCTION_WEIGHT:
            self._generate_function(option)
        else:
            self._generate_proprty(option)

    def _noterm_comparator(self, option):
        last_part = option.parts[-1]
        operator = weighted_random(last_part['operand'].operators.items())
        last_part['operator'] = operator
        option.string += ' ' + operator + ' '

    def _noterm_value(self, option):
        last_part = option.parts[-1]
        value = last_part['operand'].generate()
        last_part['value'] = value
        option.string += value

    def _noterm_next(self, option):
        if self._parenthesis_count != 0 and random.random() < 0.5:
            self._parenthesis_count -= 1
            option.string += ')'
        if random.random() < 0.8:
            self._noterm_logical(option)
            self._noterm_part(option)

    def _noterm_logical(self, option):
        operator = weighted_random(LOGICAL_OPERATORS.items())
        logical_operator = LogicalOperator(operator)
        last_part = option.parts[-1]
        logical_operator.part_one_id = last_part['id']
        option.add_logical(LogicalOperator(operator))
        option.string += ' ' + operator + ' '

    def _generate_function(self, option):
        functions_wrapper = random.choice(list(self._functions.group.values()))
        functions_dict = get_methods_dict(functions_wrapper.__class__)
        function_call = random.choice(list(functions_dict.values()))

        generated_function = function_call(functions_wrapper)
        last_part = option.parts[-1]
        last_part['operand'] = generated_function
        option.string += generated_function.generated_string

    def _generate_proprty(self, option):
        proprty = random.choice(self.entity_set.entity_type.proprties())
        last_part = option.parts[-1]
        last_part['operand'] = proprty
        option.string += proprty.name


class Option(object):
    def __init__(self):
        self._string = ''
        self._logicals = []
        self._parts = []

    @property
    def string(self):
        return self._string

    @property
    def logicals(self):
        return self._logicals

    @property
    def parts(self):
        return self._parts

    @string.setter
    def string(self, value):
        self._string = value

    def add_logical(self, logical):
        self._logicals.append(logical)

    def add_part(self, part):
        self._parts.append(part)


class LogicalOperator(object):
    def __init__(self, operator):
        self._id = str(uuid.UUID(int=random.getrandbits(128), version=4))
        self._operator = operator
        self._part_one_id = None
        self._part_two_id = None

    @property
    def id(self):
        return self._id

    @property
    def operator(self):
        return self._operator

    @property
    def part_one_id(self):
        return self._part_one_id

    @property
    def part_two_id(self):
        return self._part_two_id

    @part_one_id.setter
    def part_one_id(self, value):
        self._part_one_id = value

    @part_two_id.setter
    def part_two_id(self, value):
        self._part_two_id = value


class FilterFunctionsGroup(object):
    def __init__(self, filterable_proprties, exclude_restrictions):
        self._group = {}
        self._init_functions_group(filterable_proprties)

        if self._group:
            self._apply_restrictions(exclude_restrictions)

    @property
    def group(self):
        return self._group

    def _init_functions_group(self, filterable_proprties):
        for proprty in filterable_proprties:
            if proprty.typ.name == 'Edm.String':
                self._group.setdefault('String', StringFilterFunctions()).add_proprty(proprty)
            elif proprty.typ.name == 'Edm.Date':
                self._group.setdefault('Date', DateFilterFunctions()).add_proprty(proprty)
            elif proprty.typ.name == 'Edm.Decimal':
                self._group.setdefault('Math', DateFilterFunctions()).add_proprty(proprty)

    def _apply_restrictions(self, exclude_restrictions):
        restricted_functions = exclude_restrictions.get(GLOBAL_FUNCTION, None)
        if restricted_functions:
            self._delete_restricted_functions(restricted_functions)

    def _delete_restricted_functions(self, restricted_functions):
        for functions_wrapper in self._group.values():
            methods_dict = get_methods_dict(functions_wrapper)
            for restricted_function in restricted_functions:
                method_name = 'func_' + restricted_function
                if method_name in methods_dict:
                    delattr(functions_wrapper.__class__, method_name)


class DateFilterFunctions(object):
    def __init__(self):
        self._probability = DATE_FUNC_PROB
        self._proprties = []

    @property
    def proprties(self):
        return self._proprties

    @property
    def probability(self):
        return self._probability

    @probability.setter
    def probability(self, probability_number):
        self._probability = probability_number

    def add_proprty(self, proprty_object):
        self._proprties.append(proprty_object)

    def func_day(self):
        proprty = random.choice(self._proprties)
        generated_string = 'day({})'.format(proprty.name)
        return FilterFunction([proprty], None, generated_string, FunctionsInt('day'))

    def func_hour(self):
        proprty = random.choice(self._proprties)
        generated_string = 'hour({})'.format(proprty.name)
        return FilterFunction([proprty], None, generated_string, FunctionsInt('hour'))

    def func_minute(self):
        proprty = random.choice(self._proprties)
        generated_string = 'minute({})'.format(proprty.name)
        return FilterFunction([proprty], None, generated_string, FunctionsInt('minute'))

    def func_month(self):
        proprty = random.choice(self._proprties)
        generated_string = 'month({})'.format(proprty.name)
        return FilterFunction([proprty], None, generated_string, FunctionsInt('month'))

    def func_second(self):
        proprty = random.choice(self._proprties)
        generated_string = 'second({})'.format(proprty.name)
        return FilterFunction([proprty], None, generated_string, FunctionsInt('second'))

    def func_year(self):
        proprty = random.choice(self._proprties)
        generated_string = 'year({})'.format(proprty.name)
        return FilterFunction([proprty], None, generated_string, FunctionsInt('second'))


class MathFilterFunctions(object):
    def __init__(self):
        self._probability = MATH_FUNC_PROB
        self._proprties = []

    @property
    def proprties(self):
        return self._proprties

    @property
    def probability(self):
        return self._probability

    @probability.setter
    def probability(self, probability_number):
        self._probability = probability_number

    def add_proprty(self, proprty_object):
        self._proprties.append(proprty_object)

    def func_round(self):
        proprty = random.choice(self._proprties)
        generated_string = 'round({})'.format(proprty.name)
        return FilterFunction([proprty], None, generated_string, FunctionsInt('round'))

    def func_floor(self):
        proprty = random.choice(self._proprties)
        generated_string = 'floor({})'.format(proprty.name)
        return FilterFunction([proprty], None, generated_string, FunctionsInt('floor'))

    def func_ceiling(self):
        proprty = random.choice(self._proprties)
        generated_string = 'ceiling({})'.format(proprty.name)
        return FilterFunction([proprty], None, generated_string, FunctionsInt('ceiling'))


class StringFilterFunctions(object):
    def __init__(self):
        self._probability = STRING_FUNC_PROB
        self._proprties = []

    @property
    def proprties(self):
        return self._proprties

    @property
    def probability(self):
        return self._probability

    @probability.setter
    def probability(self, probability_number):
        self._probability = probability_number

    def add_proprty(self, proprty_object):
        self._proprties.append(proprty_object)

    def func_substringof(self):
        proprty = random.choice(self._proprties)
        value = proprty.generate()
        generated_string = 'substringof({}, {})'.format(proprty.name, value)
        return FilterFunction([proprty], [value], generated_string, FunctionsBool('substringof'))

    def func_endswith(self):
        proprty = random.choice(self._proprties)
        value = proprty.generate()
        generated_string = 'endswith({}, {})'.format(proprty.name, value)
        return FilterFunction([proprty], [value], generated_string, FunctionsBool('endswith'))

    def func_startswith(self):
        proprty = random.choice(self._proprties)
        value = proprty.generate()
        generated_string = 'startswith({}, {})'.format(proprty.name, value)
        return FilterFunction([proprty], [value], generated_string, FunctionsBool('startswith'))

    def func_length(self):
        proprty = random.choice(self._proprties)
        value = proprty.generate()
        generated_string = 'length({})'.format(proprty.name)
        return FilterFunction([proprty], [value], generated_string, FunctionsInt('length'))

    def func_indexof(self):
        proprty = random.choice(self._proprties)
        value = proprty.generate()
        generated_string = 'indexof({}, {})'.format(proprty.name, value)
        return FilterFunction([proprty], [value], generated_string, FunctionsInt('indexof'))

    def func_replace(self):
        proprty = random.choice(self._proprties)
        self_mock = type('', (), {'max_string_length': 5})
        literal1 = RandomGenerator.edm_string(self_mock)
        literal2 = RandomGenerator.edm_string(self_mock)
        generated_string = 'replace({}, {}, {})'.format(proprty.name, literal1, literal2)
        return FilterFunction([proprty], [literal1, literal2], generated_string,
                              FunctionsString('replace'))

    def func_substring(self):
        proprty = random.choice(self._proprties)
        int1 = RandomGenerator.edm_byte()
        if random.random() > 0.5:
            int2 = RandomGenerator.edm_byte()
            param_list = [int1, int2]
            generated_string = 'substring({}, {}, {})'.format(proprty.name, int1, int2)
        else:
            param_list = [int1]
            generated_string = 'substring({}, {})'.format(proprty.name, int1)
        return FilterFunction([proprty], param_list, generated_string, FunctionsString('substring'))

    def func_tolower(self):
        proprty = random.choice(self._proprties)
        generated_string = 'tolower({})'.format(proprty.name)
        return FilterFunction([proprty], None, generated_string, FunctionsString('tolower'))

    def func_toupper(self):
        proprty = random.choice(self._proprties)
        generated_string = 'toupper({})'.format(proprty.name)
        return FilterFunction([proprty], None, generated_string, FunctionsString('toupper'))

    def func_trim(self):
        proprty = random.choice(self._proprties)
        generated_string = 'trim({})'.format(proprty.name)
        return FilterFunction([proprty], None, generated_string, FunctionsString('trim'))

    def func_concat(self):
        proprty = random.choice(self._proprties)
        if random.random() > 0.5:
            self_mock = type('', (), {'max_string_length': 20})
            value = RandomGenerator.edm_string(self_mock)
            proprty_list = [proprty]
            param_list = [value]
            generated_string = 'concat({}, {})'.format(proprty.name, value)
        else:
            proprty2 = random.choice(self._proprties)
            proprty_list = [proprty, proprty2]
            param_list = None
            generated_string = 'concat({}, {})'.format(proprty.name, proprty2.name)
        return FilterFunction(proprty_list, param_list, generated_string,
                              FunctionsString('concat'))


class FunctionsReturnType(object):
    def __init__(self, return_type, operators, name, generator):
        self._return_type = return_type
        self._operators = operators
        self._name = name
        self._generator = generator

    @property
    def return_type(self):
        return self._return_type

    @property
    def operators(self):
        return self._operators

    @property
    def name(self):
        return self._name

    def generate(self):
        return self._generator()


class FunctionsInt(FunctionsReturnType):
    def __init__(self, name):
        super(FunctionsInt, self).__init__('Edm.Int32', EXPRESSION_OPERATORS,
                                           name, RandomGenerator.edm_int32)


class FunctionsString(FunctionsReturnType):
    def __init__(self, name):
        self._self_mock = namedtuple('self_mock', 'max_string_length')
        super(FunctionsString, self).__init__('Edm.String', EXPRESSION_OPERATORS,
                                              name, RandomGenerator.edm_string)

    def generate(self):
        return self._generator(self._self_mock(10))


class FunctionsBool(FunctionsReturnType):
    def __init__(self, name):
        super(FunctionsBool, self).__init__('Edm.Boolean', BOOLEAN_OPERATORS,
                                            name, RandomGenerator.edm_boolean)


class FilterFunction(object):
    def __init__(self, proprties, params, generated_string, function_type):
        self._proprties = proprties
        self._params = params
        self._generated_string = generated_string
        self._function_type = function_type

    @property
    def proprties(self):
        return self._proprties

    @property
    def params(self):
        return self._params

    @property
    def generated_string(self):
        return self._generated_string

    @property
    def operators(self):
        return self._function_type.operators

    def generate(self):
        return self._function_type.generate()


def is_method(obj):
    return inspect.isfunction(obj) or inspect.ismethod(obj)


def get_methods_dict(class_object):
    filter_functions = inspect.getmembers(class_object, predicate=is_method)
    return {name: method for name, method in filter_functions if name.startswith('func_')}


def weighted_random(items):
    random_number = random.random()
    for value, weight in items:
        if random_number < weight:
            return value
        random_number -= weight
    return None
