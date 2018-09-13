"""This module contains core parts of the fuzzer and additional handler classes."""

import random
import io
import os
import sys
import logging
import gevent
import requests
import requests.adapters

from copy import deepcopy
from datetime import datetime
from collections import namedtuple
from abc import ABCMeta, abstractmethod
from lxml import etree
from gevent.pool import Pool
from bson.objectid import ObjectId

from pyodata.v2.model import NAMESPACES
from odfuzz.entities import Builder, FilterOptionBuilder, FilterOptionDeleter, FilterOption, \
    OrderbyOptionBuilder, OrderbyOption, KeyValuesBuilder
from odfuzz.restrictions import RestrictionsGroup
from odfuzz.statistics import Stats
from odfuzz.mongos import MongoClient
from odfuzz.mutators import NumberMutator, StringMutator
from odfuzz.exceptions import DispatcherError
from odfuzz.config import Config
from odfuzz.constants import *

SelfMock = namedtuple('SelfMock', 'max_length')


class Manager(object):
    """A class for managing the fuzzer runtime."""

    def __init__(self, arguments, collection_name):
        self._dispatcher = Dispatcher(arguments, has_certificate=True)
        self._async = getattr(arguments, 'async')
        Config.retrieve_config()

        restrictions_file = getattr(arguments, 'restr')
        if restrictions_file:
            self._restrictions = RestrictionsGroup(restrictions_file)
        else:
            self._restrictions = None

        self._collection_name = collection_name

    def start(self):
        print('Collection: {}'.format(self._collection_name))
        print('Initializing queryable entities...')
        builder = Builder(self._dispatcher, self._restrictions)
        entities = builder.build()

        print('Fuzzing...')
        fuzzer = Fuzzer(self._dispatcher, entities, self._collection_name, async=self._async)
        fuzzer.run()


class Fuzzer(object):
    """A main class that initiates a fuzzing process."""

    def __init__(self, dispatcher, entities, collection_name, **kwargs):
        self._logger = logging.getLogger(FUZZER_LOGGER)
        self._stats_logger = StatsLogger()

        self._dispatcher = dispatcher
        self._entities = entities

        self._logger.info('mongoDB collection set to {}'.format(collection_name))
        self._collection_name = collection_name
        self._mongodb = MongoClient(collection_name)
        self._analyzer = Analyzer(self._mongodb)
        self._selector = Selector(self._mongodb, self._entities)

        self._async = kwargs.get('async')
        if self._async:
            self._queryable_factory = MultipleQueryable
            self._dispatch = self._get_multiple_responses
        else:
            self._queryable_factory = SingleQueryable
            self._dispatch = self._get_single_response

        Stats.tests_num = 0
        Stats.fails_num = 0
        Stats.exceptions_num = 0

        # This step is required to redirect printing of stack trace by greenlets. I haven't
        # found any other conventional way to suppress such a printing. In the past, it was
        # possible to set which type of exceptions shouldn't be printed by:
        # gevent.hub.Hub.NOT_ERROR=(Exception,)
        # Source: https://github.com/gevent/gevent/issues/55
        #
        # If anybody in the future will want to print output to the standard error output,
        # he/she will be required to set sys.stderr back to its default value by:
        # sys.stderr = sys.__stderr__
        # Source: https://docs.python.org/3/library/sys.html#sys.__stderr__
        sys.stderr = LoggerErrorWritter(self._logger)

    def run(self):
        time_seed = datetime.now()
        random.seed(time_seed, version=1)
        self._logger.info('Seed is set to \'{}\''.format(time_seed))

        self._mongodb.remove_collection()
        self.seed_population()
        if self._mongodb.total_queries() == 0:
            self._logger.info('There are no queries generated yet.')
            sys.stdout.write('OData service does not contain any queryable entities. Exiting...\n')
            sys.exit(0)

        self._selector.score_average = self._mongodb.overall_score() / self._mongodb.total_queries()
        self.evolve_population()

    def seed_population(self):
        self._logger.info('Seeding population with requests...')
        for queryable in self._entities.all():
            seed_range = len(queryable.entity_set.entity_type.proprties()) * Config.seed_size
            if self._async:
                seed_range = round(seed_range / Config.pool_size)
            self._logger.info('Population range for entity \'{}\' is set to {}'
                              .format(queryable.entity_set.name, seed_range))
            for _ in range(seed_range):
                q = self._queryable_factory(queryable, self._logger)
                queries = q.generate()
                self._send_queries(queries)
                self._analyze_queries(queries)
                self._save_queries(queries)

    def evolve_population(self):
        self._logger.info('Evolving population of requests...')
        while True:
            selection = self._selector.select()
            if selection.crossable:
                self._logger.info('Crossing parents...')
                q = self._queryable_factory(selection.queryable, self._logger)
                queries = q.crossover(selection.crossable)
                self._send_queries(queries)
                analyzed_queries = self._analyze_queries(queries)
                self._remove_weak_queries(analyzed_queries, queries)
            else:
                self._logger.info('Generating new queries...')
                q = self._queryable_factory(selection.queryable, self._logger)
                queries = q.generate()
                self._send_queries(queries)
                self._analyze_queries(queries)
                self._slay_weakest_individuals(len(queries))
            self._save_queries(queries)

    def _save_queries(self, queries):
        self._stats_logger.log_stats(queries)
        self._save_to_database(queries)
        print_tests_num()

    def _send_queries(self, queries):
        while True:
            success = self._dispatch(queries)
            if success:
                break

    def _get_multiple_responses(self, queries):
        pool = Pool(Config.pool_size)
        for query in queries:
            pool.spawn(self._get_response, query)
        try:
            pool.join(raise_error=True)
        except DispatcherError:
            pool.kill()
            self._handle_dispatcher_exception()
            return False
        return True

    def _get_single_response(self, queries):
        query = queries[0]
        try:
            self._get_response(query)
        except DispatcherError:
            self._handle_dispatcher_exception()
            return False
        return True

    def _get_response(self, query):
        query.response = self._dispatcher.get(query.query_string, timeout=REQUEST_TIMEOUT)
        if query.response.status_code != 200:
            self._set_error_attributes(query)
            Stats.fails_num += 1
        else:
            setattr(query.response, 'error_code', '')
            setattr(query.response, 'error_message', '')

    def _handle_dispatcher_exception(self):
        Stats.exceptions_num += 1
        print_tests_num()
        self._logger.info('Retrying in {} seconds...'.format(RETRY_TIMEOUT))
        gevent.sleep(RETRY_TIMEOUT)

    def _analyze_queries(self, queries):
        analyzed_offsprings = []
        for query in queries:
            analyzed_offsprings.append(self._analyzer.analyze(query))
        return analyzed_offsprings

    def _remove_weak_queries(self, analyzed_offsprings, queries):
        for offspring in analyzed_offsprings:
            offspring.slay_weak_individual(self._mongodb, queries)

    def _slay_weakest_individuals(self, number_of_individuals):
        self._mongodb.remove_weakest_queries(number_of_individuals)

    def _save_to_database(self, queries):
        for query in queries:
            self._mongodb.save_document(query.dictionary)

    def _set_error_attributes(self, query):
        self._set_attribute_value(query, 'error_code', 'error', 'code')
        self._set_attribute_value(query, 'error_message', 'error', 'message')

    def _set_attribute_value(self, query, attr, *args):
        try:
            json = query.response.json()
            value = self._get_attr_from_json(json, *args)
        except ValueError:
            value = self._get_attr_from_xml(query.response.content, *args)
        setattr(query.response, attr, value)

    def _get_attr_from_json(self, json, *args):
        for arg in args:
            json = json[arg]
        if 'value' in json:
            json = json['value']
        self._logger.info('Fetched \'{}\' from JSON'.format(json))
        return json

    def _get_attr_from_xml(self, content, *args):
        try:
            parsed_etree = etree.parse(io.BytesIO(content))
        except etree.XMLSyntaxError as xml_ex:
            self._logger.info('An exception was raised while parsing the XML: {}'.format(xml_ex))
            return ''
        xpath_string = build_xpath_format_string(*args)
        value = parsed_etree.xpath(xpath_string, namespaces=NAMESPACES)[0]
        self._logger.info('Fetched \'{}\' from XML'.format(value))
        return value


class Queryable(object):
    def __init__(self, queryable, logger):
        self._queryable = queryable
        self._logger = logger

    def generate_query(self):
        accessible_entity = self._queryable.get_accessible_entity_set()
        query = Query(accessible_entity)
        self.generate_options(query)
        Stats.tests_num += 1
        return query

    def generate_options(self, query):
        depending_data = {}
        if query.targets_single_entity():
            options_list = self._queryable.random_single_entity_options()
        else:
            options_list = self._queryable.random_options()

        for option in options_list:
            generated_option = option.generate(depending_data)
            query.add_option(option.name, generated_option.data)
            depending_data[option.name] = option.get_depending_data()
        query.build_string()
        self._logger.info('Generated query \'{}\''.format(query.query_string))

    def _crossover_queries(self, query1, query2):
        if is_filter_crossable(query1, query2):
            replaceable_parts = [part for part in query1['_$filter']['parts'] if part.get('replaceable', True)]
            if replaceable_parts:
                offspring = self._crossover_filter(replaceable_parts, query1, query2)
            else:
                offspring = self._crossover_options(query1, query2)
        else:
            offspring = self._crossover_options(query1, query2)
        Stats.created_by_crossover += 1
        query = self.build_offspring(deepcopy(offspring))
        self._mutate_query(query)
        query.add_predecessor(query1['_id'])
        query.add_predecessor(query2['_id'])
        query.build_string()
        self._logger.info('Generated {}'.format(query.query_string))
        Stats.tests_num += 1
        return query

    def _crossover_filter(self, replaceable_parts, query1, query2):
        filter_option2 = query2['_$filter']

        # properties that are not required for draft entities are replaceable by default
        part_to_replace = random.choice(replaceable_parts)
        replacing_part = random.choice(filter_option2['parts'])

        if 'func' in replacing_part:
            part_to_replace['func'] = replacing_part['func']
            part_to_replace['params'] = replacing_part['params']
            part_to_replace['proprties'] = replacing_part['proprties']
            part_to_replace['return_type'] = replacing_part['return_type']
        else:
            if 'func' in part_to_replace:
                part_to_replace.pop('func')
                part_to_replace.pop('params')
                part_to_replace.pop('proprties')
                part_to_replace.pop('return_type')

        part_to_replace['name'] = replacing_part['name']
        part_to_replace['operator'] = replacing_part['operator']
        part_to_replace['operand'] = replacing_part['operand']

        return query1

    def build_offspring(self, offspring):
        accessible_entity = self._queryable.get_accessible_entity_set()
        query = Query(accessible_entity)
        for option in offspring['order']:
            query.add_option(option[1:], offspring[option])
        return query

    def _crossover_options(self, query1, query2):
        filled_options = [option_name for option_name, value in query2.items()
                          if value is not None and option_name.startswith('_$')]
        selected_option = random.choice(filled_options)
        if selected_option not in query1['order']:
            query1['order'].append(selected_option)
        query1[selected_option] = query2[selected_option]
        return query1

    def _mutate_query(self, query):
        option_name, option_value = random.choice(list(query.options.items()))
        if query.is_option_deletable(option_name) and len(query.order) > 1 and random.random() < OPTION_DEL_PROB:
            query.delete_option(option_name)
        else:
            self._mutate_option(query, option_name, option_value)
        Stats.created_by_mutation += 1

    def build_mutated_accessible_keys(self, accessible_keys, data_to_be_mutated):
        self._mutate_accessible_keys(accessible_keys, data_to_be_mutated)
        query = self.build_offspring(data_to_be_mutated)
        query.add_predecessor(data_to_be_mutated['_id'])
        query.build_string()
        return query

    def _mutate_accessible_keys(self, accessible_keys, entity_data):
        keys_list = list(accessible_keys.items())
        key_values = random.sample(keys_list, round((random.random() * (len(keys_list) - 1)) + 1))
        if entity_data['accessible_set']:
            accessible_entity_set = self._queryable.principal_entity(entity_data['accessible_set'])
        else:
            accessible_entity_set = self._queryable.entity_set

        for proprty_name, value in key_values:
            accessible_keys[proprty_name] = '\'' + accessible_entity_set.entity_type.proprty(proprty_name) \
                .mutate(value[1:-1]) + '\''

    def _mutate_option(self, query, option_name, option_value):
        if option_name == FILTER:
            if option_value['logicals'] and random.random() < FILTER_DEL_PROB:
                logical_index = round(random.random() * (len(option_value['logicals']) - 1))
                parts = self._get_removable_parts(option_value, logical_index)
                if parts:
                    random_part = random.choice(parts)
                    self._remove_logical_part(option_value, logical_index, random_part)
                else:
                    self._mutate_filter_part(option_name, option_value)
            else:
                self._mutate_filter_part(option_name, option_value)
        elif option_name == ORDERBY:
            self._mutate_orderby_part(option_value)
        elif option_name == EXPAND:
            # TODO: implement mutator for expand method
            pass
        elif option_name == SEARCH:
            # TODO: implement mutator for search method
            pass
        else:
            query.options[option_name] = self._mutate_value(NumberMutator, option_value)

    def _get_removable_parts(self, option_value, logical_index):
        logical = option_value['logicals'][logical_index]
        removable_ids = []
        if is_removable(option_value, logical['left_id']):
            removable_ids.append('left_id')
        if is_removable(option_value, logical['right_id']):
            removable_ids.append('right_id')
        return removable_ids

    def _remove_logical_part(self, option_value, index, adjacent_id):
        logical = option_value['logicals'].pop(index)
        FilterOptionDeleter(option_value, logical).remove_adjacent(adjacent_id)

    def _mutate_filter_part(self, option_name, option_value):
        part = random.choice(option_value['parts'])
        if 'func' in part:
            self._mutate_filter_function(part, option_name)
        else:
            proprty = self._queryable.query_option(option_name).entity_set.entity_type.proprty(part['name'])
            if getattr(proprty, 'mutate', None):
                part['operand'] = proprty.mutate(part['operand'])

    def _mutate_filter_function(self, part, option_name):
        if part['params'] and random.random() < 0.5:
            # TODO: mutate more than one parameter
            proprty = self._queryable.query_option(option_name).entity_set.entity_type.proprty(part['proprties'][0])
            part['params'][0] = proprty.mutate(part['params'][0])
        else:
            if part['return_type'] == 'Edm.Boolean':
                part['operand'] = 'true' if part['operand'] == 'false' else 'false'
            elif part['return_type'] == 'Edm.String':
                part['operand'] = self._mutate_value(StringMutator, part['operand'], SelfMock(max_length=5))
                part['operand'] = '\'' + part['operand'] + '\''
            elif part['return_type'].startswith('Edm.Int'):
                part['operand'] = self._mutate_value(NumberMutator, part['operand'])

    def _mutate_orderby_part(self, option_value):
        proprties_num = len(option_value) - 1
        if proprties_num > 1 and random.random() < ORDERBY_DEL_PROB:
            remove_index = round(random.random() * proprties_num)
            del option_value[remove_index]

        self._mutate_proprty_order(option_value)

    def _mutate_proprty_order(self, option_value):
        random_proprty = random.choice(option_value)
        current_order = random_proprty[1]
        possible_orders = {'asc', 'desc', ''}
        possible_orders.remove(current_order)
        random_proprty[1] = random.choice(list(possible_orders))

    def _mutate_value(self, mutator_class, value, self_mock=None):
        mutators = self._get_mutators(mutator_class)
        mutator = random.choice(mutators)
        mutated_value = getattr(mutator_class, mutator)(self_mock, value)
        return mutated_value

    def _get_mutators(self, mutators_class):
        mutators = []
        for func_name in mutators_class.__dict__.keys():
            if not func_name.startswith('_'):
                mutators.append(func_name)
        return mutators


class MultipleQueryable(Queryable):
    def generate(self):
        queries = []
        for _ in range(Config.pool_size):
            query = self.generate_query()
            if query:
                queries.append(query)
        return queries

    def crossover(self, crossable_selection):
        children = []
        for _ in range(Config.pool_size):
            accessible_keys = crossable_selection[0].get('accessible_keys', None)
            if accessible_keys and random.random() <= KEY_VALUES_MUTATION_PROB:
                query = self.build_mutated_accessible_keys(accessible_keys, crossable_selection[0])
                children.append(query)
                Stats.tests_num += 1
                Stats.created_by_mutation += 1
            else:
                query1, query2 = crossable_selection
                offspring = self._crossover_queries(query1, query2)
                if offspring:
                    children.append(offspring)
        return children


class SingleQueryable(Queryable):
    def generate(self):
        query = self.generate_query()
        return [query]

    def crossover(self, crossable_selection):
        query1, query2 = crossable_selection
        accessible_keys = crossable_selection[0].get('accessible_keys', None)
        if accessible_keys and random.random() <= KEY_VALUES_MUTATION_PROB:
            query = self.build_mutated_accessible_keys(accessible_keys, crossable_selection[0])
            Stats.tests_num += 1
            Stats.created_by_mutation += 1
        else:
            query = self._crossover_queries(query1, query2)
        return [query]


class StatsLogger(object):
    def __init__(self):
        self._stats_logger = logging.getLogger(STATS_LOGGER)
        self._filter_logger = logging.getLogger(FILTER_LOGGER)
        self._stats_logger.info(CSV)
        self._filter_logger.info(CSV_FILTER)

    def log_stats(self, queries):
        self.log_overall(queries)
        self.log_filter(queries)

    def log_overall(self, queries):
        for query in queries:
            query_dict = query.dictionary
            query_proprties = self._get_proprties(query_dict)
            for proprty in query_proprties:
                self._log_formatted_stats(query, query_dict, proprty)

    def _log_formatted_stats(self, query, query_dict, proprty):
        self._stats_logger.info(
            '{StatusCode};{ErrorCode};"{ErrorMessage}";{EntitySet};{AccessibleSet};{AccessibleKeys};'
            '{Property};{orderby};{top};{skip};"{filter}";{expand};"{search}"'.format(
                StatusCode=query.response.status_code,
                ErrorCode=query.response.error_code,
                ErrorMessage=query.response.error_message.replace('"', '""'),
                EntitySet=query_dict['entity_set'],
                AccessibleSet=query_dict['accessible_set'],
                AccessibleKeys=KeyValuesBuilder.build_string(query_dict['accessible_keys']),
                Property=proprty,
                orderby=query.options_strings['$orderby'],
                top=query.options_strings['$top'],
                skip=query.options_strings['$skip'],
                filter=query.options_strings['$filter'].replace('"', '""'),
                expand=query.options_strings['$expand'],
                search=query.options_strings['search'].replace('"', '""')
            )
        )

    def _get_proprties(self, query_dict):
        proprties = set()
        filter_option = query_dict.get('_$filter')
        if filter_option:
            proprties.update(self._get_filter_proprties(filter_option))
        orderby_option = query_dict.get('_$orderby')
        if orderby_option:
            for proprty, _ in orderby_option:
                proprties.update([proprty])
        if not proprties:
            return [None]
        else:
            return list(proprties)

    def _get_filter_proprties(self, filter_option):
        proprties = set()
        for part in filter_option['parts']:
            if 'func' in part:
                for proprty in part['proprties']:
                    proprties.update([proprty])
            else:
                proprties.update([part['name']])
        return proprties

    def log_filter(self, queries):
        for query in queries:
            filter_option = query.dictionary.get('_$filter')
            if filter_option:
                logical_names = set([logical['name'] for logical in filter_option['logicals']])
                if 'and' in logical_names and 'or' in logical_names:
                    logical = 'combination'
                else:
                    if filter_option['logicals']:
                        logical = filter_option['logicals'][0]['name']
                    else:
                        logical = ''
                self._log_filter_parts(filter_option, query, logical)

    def _log_filter_parts(self, filter_option, query, logical_name):
        for part in filter_option['parts']:
            if 'func' in part:
                for proprty in part['proprties']:
                    self._log_formatted_filter(query, proprty, logical_name, part, part['func'])
            else:
                proprty = part['name']
                self._log_formatted_filter(query, proprty, logical_name, part, '')

    def _log_formatted_filter(self, query, proprty, logical_name, part, func):
        self._filter_logger.info(
            '{StatusCode};{ErrorCode};"{ErrorMessage}";{EntitySet};{Property};{logical};'
            '{operator};{function};"{operand}"'.format(
                StatusCode=query.response.status_code,
                ErrorCode=query.response.error_code,
                ErrorMessage=query.response.error_message.replace('"', '""'),
                EntitySet=query.dictionary['entity_set'],
                Property=proprty,
                logical=logical_name,
                operator=part['operator'],
                function=func,
                operand=part['operand'].replace('"', '""')
            )
        )


class Selector(object):
    def __init__(self, mongodb, entities):
        self._logger = logging.getLogger(FUZZER_LOGGER)
        self._mongodb = mongodb
        self._score_average = 0
        self._passed_iterations = 0
        self._entities = entities

    def select(self):
        if self._is_score_stagnating():
            selection = Selection(None, random.choice(list(self._entities.all())), self._score_average)
        else:
            selection = self._crossable_selection()
        self._passed_iterations += 1

        return selection

    def _crossable_selection(self):
        queryable = random.choice(list(self._entities.all()))
        crossable = self._get_crossable(queryable)
        selection = Selection(crossable, queryable, self._score_average)
        return selection

    def _is_score_stagnating(self):
        if self._passed_iterations > ITERATIONS_THRESHOLD:
            self._passed_iterations = 0
            current_average = self._mongodb.overall_score() / self._mongodb.total_queries()
            old_average = self._score_average
            self._score_average = current_average
            if (current_average - old_average) < SCORE_EPS:
                return True
        return False

    def _get_crossable(self, queryable):
        entity_set_name = queryable.entity_set.name
        parent1 = self._mongodb.best_filter_sample_query(entity_set_name, None)
        if parent1 is None:
            return None
        parent2 = self._mongodb.best_filter_sample_query(entity_set_name, ObjectId(parent1['_id']))
        if parent2 is None:
            return None
        return parent1, parent2


class Selection(object):
    """A container that holds objects created by Selector."""

    def __init__(self, crossable, queryable, score_average):
        self._crossable = crossable
        self._queryable = queryable
        self._score_average = score_average

    @property
    def crossable(self):
        return self._crossable

    @property
    def queryable(self):
        return self._queryable

    @property
    def score_average(self):
        return self._score_average


class Analyzer(object):
    """An analyzer for analyzing generated queries."""

    def __init__(self, mongodb):
        self._mongodb = mongodb
        self._population_score = 0

    def analyze(self, query):
        new_score = FitnessEvaluator.evaluate(query)
        query.score = new_score
        self._update_population_score(new_score)
        predecessors_ids = query.dictionary['predecessors']
        if predecessors_ids:
            offspring = self._build_offspring_by_score(predecessors_ids, query, new_score)
        else:
            offspring = EmptyOffspring()
        return offspring

    def _build_offspring_by_score(self, predecessors_id, query, new_score):
        for predecessor_id in predecessors_id:
            if self._mongodb.query_by_id(predecessor_id)['score'] < new_score:
                return BetterOffspring(predecessor_id)
        return WorseOffspring(query)

    def _update_population_score(self, query_score):
        if self._population_score == 0:
            self._population_score = self._mongodb.overall_score()
        else:
            self._population_score += query_score


class Offspring(metaclass=ABCMeta):
    @abstractmethod
    def slay_weak_individual(self, mongodb, queries):
        pass

    @abstractmethod
    def get_number_of_slayed(self):
        pass


class BetterOffspring(Offspring):
    def __init__(self, worse_predecessor_id):
        self._worse_predecessor_id = worse_predecessor_id
        self._slayed = 0

    def slay_weak_individual(self, mongodb, queries):
        deleted_num = mongodb.remove_by_id(self._worse_predecessor_id)
        if deleted_num == 0:
            mongodb.remove_weakest_queries(1)
        self._slayed = 1

    def get_number_of_slayed(self):
        return self._slayed


class WorseOffspring(Offspring):
    def __init__(self, offspring):
        self._offspring = offspring
        self._slayed = 0

    def slay_weak_individual(self, mongodb, queries):
        queries.remove(self._offspring)
        self._slayed = 1

    def get_number_of_slayed(self):
        return self._slayed


class EmptyOffspring(Offspring):
    def slay_weak_individual(self, mongodb, queries):
        mongodb.remove_weakest_queries(1)

    def get_number_of_slayed(self):
        return 1


class FitnessEvaluator(object):
    """A group of heuristic functions."""

    @staticmethod
    def evaluate(query):
        total_score = 0
        keys_len = sum(len(option_name) for option_name in query.options.keys())
        query_len = len(query.query_string) - len(query.entity_name) - keys_len
        total_score += FitnessEvaluator.eval_string_length(query_len)
        total_score += FitnessEvaluator.eval_http_status_code(
            query.response.status_code, query.response.error_code, query.response.error_message)
        total_score += FitnessEvaluator.eval_http_response_time(query.response)
        return total_score

    @staticmethod
    def eval_http_status_code(status_code, error_code, error_message):
        if status_code == 500:
            return SAPErrors.evaluate(error_code, error_message)
        elif status_code == 200:
            return 0
        else:
            return -50

    @staticmethod
    def eval_http_response_time(response):
        if not response.headers.get('content-length'):
            return 0
        if int(response.headers['content-length']) > CONTENT_LEN_SIZE:
            return -10
        total_seconds = response.elapsed.total_seconds()
        score = total_seconds / 10
        if total_seconds < 100:
            score += (total_seconds ** 2) / (10 ** (len(str(total_seconds)) + 1))
        return round(score)

    @staticmethod
    def eval_string_length(string_length):
        if string_length < 10:
            return 0
        else:
            return round(STRING_THRESHOLD / string_length)


class SAPErrors(object):
    """A container of all types of errors produced by the SAP systems."""

    @staticmethod
    def evaluate(error_code, error_message):
        if error_code == 'SY/530':
            # Wrong number of analytical ID
            if error_message.startswith('Invalid part') and error_message.endswith('of analytical ID'):
                return -50
        elif error_code == '/IWBEP/CM_MGW_RT/176':
            # Unsupported type of language
            if error_message.startswith('\'Language') and error_message.endswith('not in system\''):
                return -50
        # The interpreter cannot convert generated UTF8 character
        elif error_code == 'CONVT_CODEPAGE':
            return -10

        return 100


class Query(object):
    """A wrapper of a generated query."""

    def __init__(self, accessible_entity):
        self._accessible_entity = accessible_entity
        self._options = {}
        self._query_string = ''
        self._dict = None
        self._score = None
        self._predecessors = []
        self._order = []
        self._response = None
        self._parts = 0
        self._id = ObjectId()
        self._options_strings = {'$orderby': '', '$filter': '', '$skip': '', '$top': '', '$expand': '',
                                 'search': ''}

    @property
    def entity_name(self):
        return self._accessible_entity.entity_set_name

    @property
    def options(self):
        return self._options

    @property
    def query_string(self):
        return self._query_string

    @property
    def response(self):
        return self._response

    @property
    def dictionary(self):
        self._create_dict()
        return self._dict

    @property
    def score(self):
        return self._score

    @property
    def query_id(self):
        return self._id

    @property
    def options_strings(self):
        return self._options_strings

    @property
    def predecessors(self):
        return self._predecessors

    @property
    def order(self):
        return self._order

    @property
    def accessible_entity(self):
        return self._accessible_entity

    @query_string.setter
    def query_string(self, value):
        self._query_string = value

    @response.setter
    def response(self, value):
        self._response = value

    @score.setter
    def score(self, value):
        self._score = value

    @accessible_entity.setter
    def accessible_entity(self, value):
        self._accessible_entity = value

    def targets_single_entity(self):
        return self._accessible_entity.targets_single_entity()

    def is_option_deletable(self, name):
        return not (name == FILTER and self._accessible_entity.entity_set.requires_filter)

    def add_option(self, name, option):
        self._options[name] = option
        self._order.append('_' + name)

    def delete_option(self, name):
        self._options[name] = None
        self._order.remove('_' + name)

    def add_predecessor(self, predecessor_id):
        self._predecessors.append(predecessor_id)

    def build_string(self):
        self._query_string = self._accessible_entity.path + '?'
        for option_name in self._order:
            if option_name.endswith('filter'):
                filter_data = deepcopy(self._options[option_name[1:]])
                replace_forbidden_characters(filter_data['parts'])
                option_string = build_filter_string(filter_data)
            elif option_name.endswith('orderby'):
                orderby_data = self._options[option_name[1:]]
                orderby_option = OrderbyOption(orderby_data)
                option_string = OrderbyOptionBuilder(orderby_option).build()
            elif option_name.endswith('expand'):
                option_string = ','.join(self._options[option_name[1:]])
            else:
                option_string = self._options[option_name[1:]]
                option_string = replace_special_characters(option_string)
            self._options_strings[option_name[1:]] = option_string
            self._query_string += option_name[1:] + '=' + option_string + '&'
        self._query_string = self._query_string.rstrip('&')
        self._add_appendix()

    def _create_dict(self):
        # key fields cannot start with a dollar sign in mongoDB,
        # therefore names of query options start with an underscore;
        # in the further processing, the underscore is skipped;
        # we are doing this because the search query option introduced
        # to OData 2.0 SAP applications does not contain a dollar sign
        self._dict = {
            '_id': self._id,
            'http': str(self._response.status_code),
            'error_code': self._response.error_code,
            'error_message': self._response.error_message,
            'entity_set': self._accessible_entity.entity_set_name,
            'accessible_set': self._accessible_entity.principal_entity_name,
            'accessible_keys': self._accessible_entity.key_pairs,
            'predecessors': self._predecessors,
            'string': self._query_string,
            'score': self._score,
            'order': self._order,
            '_$orderby': self._options.get(ORDERBY),
            '_$top': self._options.get(TOP),
            '_$skip': self._options.get(SKIP),
            '_$filter': self._options.get(FILTER),
            '_$expand': self._options.get(EXPAND),
            '_search': self._options.get(SEARCH)
        }

    def _add_appendix(self):
        if Config.client:
            self._query_string += '&' + 'sap-client=' + Config.client
        if Config.format:
            self._query_string += '&' + '$format=' + Config.format


class Dispatcher(object):
    """A dispatcher for sending HTTP requests to the particular OData service."""

    def __init__(self, arguments, has_certificate=False):
        self._logger = logging.getLogger(FUZZER_LOGGER)
        self._service = arguments.service.rstrip('/') + '/'
        self._has_certificate = has_certificate

        self._session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=Config.pool_size, pool_maxsize=Config.pool_size)
        self._session.mount(ACCESS_PROTOCOL, adapter)
        self._session.verify = self._get_sap_certificate()
        self._session.headers.update({'user-agent': 'odfuzz/1.0'})
        self._init_auth_credentials(arguments.credentials)

    @property
    def session(self):
        return self._session

    @property
    def service(self):
        return self._service

    def send(self, method, query, **kwargs):
        url = self._service + query
        try:
            response = self._session.request(method, url, **kwargs)
        except requests.exceptions.RequestException as requests_ex:
            self._logger.error('An exception {} was raised'.format(requests_ex))
            raise DispatcherError('An exception was raised while sending HTTP {}: {}'
                                  .format(method, requests_ex))
        self._logger.info('Received HTTP {} from {}'.format(response.status_code, url))
        return response

    def get(self, query, **kwargs):
        return self.send('GET', query, **kwargs)

    def post(self, query, **kwargs):
        return self.send('POST', query, **kwargs)

    def _get_sap_certificate(self):
        certificate_path = None
        if self._has_certificate:
            self_dir = os.path.dirname(__file__)
            relative_path = os.path.join(os.getcwd(), CERTIFICATE_PATH)
            candidate_path = os.path.join(self_dir, relative_path)
            if not os.path.isfile(candidate_path):
                return None
            certificate_path = candidate_path
        return certificate_path

    def _init_auth_credentials(self, credentials):
        if credentials:
            try:
                username, password = credentials.split(':')
            except ValueError:
                raise DispatcherError('Entered credentials {} are not valid'.format(credentials))
            self._session.auth = (username, password)
        else:
            self._session.auth = (os.getenv(ENV_USERNAME), os.getenv(ENV_PASSWORD))


class LoggerErrorWritter:
    def __init__(self, logger):
        self._logger = logger

    def write(self, message):
        self._logger.error(message)


def is_filter_crossable(query1, query2):
    crossable = False
    if query1['order'] and query2['order'] == ['_$filter']:
        crossable = True
    if query1['_$filter'] and query2['_$filter'] and random.random() < FILTER_CROSS_PROBABILITY:
        crossable = True
    return crossable


def build_filter_string(filter_data):
    filter_option = FilterOption(filter_data['logicals'],
                                 filter_data['parts'],
                                 filter_data['groups'])
    option_string = FilterOptionBuilder(filter_option).build()
    return option_string


def replace_forbidden_characters(parts):
    for data in parts:
        if data['operand'].startswith('\''):
            data['operand'] = '\'' + replace_special_characters(data['operand'][1:-1]) + '\''
        if 'params' in data:
            if data['params']:
                for index, param in enumerate(data['params']):
                    if param.startswith('\''):
                        data['params'][index] = '\'' + replace_special_characters(param[1:-1]) + '\''


def replace_special_characters(replacing_string):
    replacing_string = replacing_string.replace('%', '%25')
    replacing_string = replacing_string.replace('&', '%26')
    replacing_string = replacing_string.replace('#', '%23')
    replacing_string = replacing_string.replace('?', '%3F')
    replacing_string = replacing_string.replace('+', '%2B')
    replacing_string = replacing_string.replace('/', '%2F')
    replacing_string = replacing_string.replace('\'', '\'\'')
    return replacing_string


def build_xpath_format_string(*args):
    xpath_string = ''
    for arg in args:
        xpath_string += '/m:{}'.format(arg)
    xpath_string += '/text()'
    return xpath_string


def print_tests_num():
    sys.stdout.flush()
    sys.stdout.write('Generated tests: {} | Failed tests: {} | Raised exceptions: {} \r'
                     .format(Stats.tests_num, Stats.fails_num, Stats.exceptions_num))


def is_removable(option_value, part_id):
    for part in option_value['parts']:
        if part['id'] == part_id:
            return part.get('replaceable', True)

    for logical in option_value['logicals']:
        if logical.get('group_id', '') == part_id:
            left_id = is_removable(option_value, logical['left_id'])
            right_id = is_removable(option_value, logical['right_id'])
            return right_id and left_id
    return True
