"""This module contains core parts of the fuzzer and additional handler classes."""

import random
import os
import sys
import logging
import operator
import requests
import requests.adapters

from datetime import datetime
from gevent.pool import Pool
from bson.objectid import ObjectId

from odfuzz.entities import Builder, FilterOptionBuilder, FilterOptionDeleter, FilterOption
from odfuzz.restrictions import RestrictionsGroup
from odfuzz.statistics import Stats, StatsPrinter
from odfuzz.mongos import MongoClient
from odfuzz.generators import NumberMutator, StringMutator
from odfuzz.exceptions import DispatcherError
from odfuzz.constants import ENV_USERNAME, ENV_PASSWORD, SEED_POPULATION, FILTER, POOL_SIZE, \
    STRING_THRESHOLD, SCORE_EPS, ITERATIONS_THRESHOLD, FUZZER_LOGGER, CLIENT, FORMAT, TOP, SKIP, \
    ORDERBY, STATS_LOGGER, FILTER_PROBABILITY, ADAPTER, FILTER_DEL_PROB


class Manager(object):
    """A class for managing the fuzzer runtime."""

    def __init__(self, arguments):
        self._dispatcher = Dispatcher(arguments.service)
        self._async = getattr(arguments, 'async')

        restrictions_file = getattr(arguments, 'restr')
        if restrictions_file:
            self._restrictions = RestrictionsGroup(restrictions_file)
        else:
            self._restrictions = None

    def start(self):
        builder = Builder(self._dispatcher, self._restrictions)
        entities = builder.build()

        fuzzer = Fuzzer(self._dispatcher, entities, async=self._async)
        fuzzer.run()


class Fuzzer(object):
    """A main class that initiates a fuzzing process."""

    def __init__(self, dispatcher, entities, **kwargs):
        self._logger = logging.getLogger(FUZZER_LOGGER)
        self._stats = logging.getLogger(STATS_LOGGER)
        self._stats.info('HTTP;Code;Message;EntitySet;Query')

        self._dispatcher = dispatcher
        self._entities = entities
        self._mongodb = MongoClient()
        self._analyzer = Analyzer(self._mongodb)
        self._selector = Selector(self._mongodb, self._entities)

        self._async = kwargs.get('async')
        if self._async:
            self._crossover = self._crossover_multiple
            self._generate = self._generate_multiple
        else:
            self._crossover = self._crossover_single
            self._generate = self._generate_single

        Stats.tests_num = 0
        Stats.fails_num = 0

        self._query_appendix = ''
        if CLIENT:
            self._query_appendix += '&' + CLIENT
        if FORMAT:
            self._query_appendix += '&' + FORMAT

    def run(self):
        time_seed = datetime.now()
        random.seed(time_seed, version=1)
        self._logger.info('Seed is set to \'{}\''.format(time_seed))
        self._mongodb.remove_collection()

        self.seed_population()
        self._selector.score_average = self._mongodb.overall_score() / self._mongodb.total_queries()
        self.evolve_population()

    def seed_population(self):
        self._logger.info('Seeding population with requests...')
        for queryable in self._entities.all():
            seed_range = len(queryable.entity_set.entity_type.proprties()) * SEED_POPULATION
            if self._async:
                seed_range = round(seed_range / POOL_SIZE)
            self._logger.info('Population range for entity \'{}\' is set to {}'
                              .format(queryable.entity_set.name, seed_range))
            for _ in range(seed_range):
                queries = self._generate(queryable)
                self._save_queries(queries)

    def evolve_population(self):
        self._logger.info('Evolving population of requests...')
        while True:
            selection = self._selector.select()
            if selection.crossable:
                self._logger.info('Crossing parents...')
                queries = self._crossover(selection.crossable, selection.queryable)
            else:
                self._logger.info('Generating new queries...')
                queries = self._generate(selection.queryable)
            self._save_queries(queries)
            self._slay_weak_individuals(selection.score_average, len(queries))

    def _save_queries(self, queries):
        self._evaluate_queries(queries)
        self._save_to_database(queries)
        self._print_tests_num()
        self._log_stats(queries)

    def _generate_multiple(self, queryable):
        queries = []
        for _ in range(POOL_SIZE):
            query = self._generate_query(queryable)
            if query:
                queries.append(query)
        if queries:
            self._get_multiple_responses(queries)
        return queries

    def _generate_single(self, queryable):
        query = self._generate_query(queryable)
        if query:
            self._get_single_response(query)
        return [query]

    def _generate_query(self, queryable):
        query = Query(queryable.entity_set.name)
        query.query_string += query.entity_name + '?'
        self._generate_options(queryable, query)
        Stats.tests_num += 1
        return query

    def _generate_options(self, queryable, query):
        for option in queryable.random_options():
            generated_option = option.generate()
            query.add_option(option.name, generated_option.data)
            query.query_string += option.name + '=' \
                                  + generated_option.option_string + '&'
        query.query_string = query.query_string.rstrip('&')
        self._logger.info('Generated query \'{}\''.format(query.query_string))

    def _crossover_multiple(self, crossable_selection, queryable):
        children = []
        for _ in range(POOL_SIZE):
            query1, query2 = crossable_selection
            offspring = self._crossover_queries(query1, query2, queryable)
            if offspring:
                children.append(offspring)
        if children:
            self._get_multiple_responses(children)
        return children

    def _crossover_single(self, crossable_selection, queryable):
        query1, query2 = crossable_selection
        query = self._crossover_queries(query1, query2, queryable)
        self._get_single_response(query)
        return [query]

    def _crossover_queries(self, query1, query2, queryable):
        if is_filter_crossable(query1, query2):
            offspring = self._crossover_filter(query1, query2)
        else:
            offspring = self._crossover_options(query1, query2)
        Stats.created_by_crossover += 1
        query = build_offspring(queryable.entity_set.name, offspring)
        self._mutate_query(query, queryable)
        query.build_string()
        query.add_predecessor(query1['_id'])
        query.add_predecessor(query2['_id'])
        self._logger.info('Generated {}'.format(query.query_string))
        Stats.tests_num += 1
        return query

    def _mutate_query(self, query, queryable):
        option_name, option_value = random.choice(list(query.options.items()))
        if option_name == FILTER:
            if random.random() < FILTER_DEL_PROB:
                status = self._remove_logical_part(option_value)
                if not status:
                    self._mutate_filter_part(queryable, option_name, option_value)
            else:
                self._mutate_filter_part(queryable, option_name, option_value)
        elif option_name == ORDERBY:
            self._mutate_orderby_part()
        else:
            query.options[option_name] = self._mutate_value(NumberMutator, option_value)
        Stats.created_by_mutation += 1

    def _remove_logical_part(self, option_value):
        if not option_value['logicals']:
            return False
        index = round(random.random() * (len(option_value['logicals']) - 1))
        logical = option_value['logicals'].pop(index)
        FilterOptionDeleter(option_value, logical).remove_adjacent()
        return True

    def _mutate_filter_part(self, queryable, option_name, option_value):
        part = random.choice(option_value['parts'])
        if 'func' in part:
            if part['params'] and random.random() < 0.5:
                proprty = queryable.query_option(option_name).entity_set.entity_type \
                    .proprty(part['proprties'][0])
                part['params'][0] = proprty.mutate(part['params'][0])
            else:
                if part['return_type'] == 'Edm.Boolean':
                    part['operand'] = 'true' if part['operand'] == 'false' else 'false'
                elif part['return_type'] == 'Edm.String':
                    part['operand'] = self._mutate_value(StringMutator, part['operand'][1:-1])
                    part['operand'] = '\'' + part['operand'] + '\''
                elif part['return_type'] == 'Edm.Int32':
                    part['operand'] = self._mutate_value(NumberMutator, part['operand'])
        else:
            proprty = queryable.query_option(option_name).entity_set.entity_type \
                .proprty(part['name'])
            part['operand'] = '\'' + proprty.mutate(part['operand'][1:-1]) + '\''

    def _mutate_orderby_part(self):
        pass

    def _mutate_value(self, mutator_class, value):
        mutators = self._get_mutators(mutator_class)
        mutator = random.choice(mutators)
        mutated_value = getattr(mutator_class, mutator)(value)
        return mutated_value

    def _get_mutators(self, mutators_class):
        mutators = []
        for func_name in mutators_class.__dict__.keys():
            if not func_name.startswith('_'):
                mutators.append(func_name)
        return mutators

    def _crossover_options(self, query1, query2):
        filled_options = [option_name for option_name, value in query2.items()
                          if value is not None and option_name.startswith('_$')]
        selected_option = random.choice(filled_options)
        if selected_option not in query1['order']:
            query1['order'].append(selected_option)
        query1[selected_option] = query2[selected_option]
        return query1

    def _crossover_filter(self, query1, query2):
        filter_option1 = query1['_$filter']
        filter_option2 = query2['_$filter']

        part_to_replace = random.choice(filter_option1['parts'])
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

    def _get_multiple_responses(self, queries):
        responses = []
        pool = Pool(POOL_SIZE)
        for query in queries:
            responses.append(pool.spawn(self._get_single_response, query))
        try:
            pool.join(raise_error=True)
        except Exception:
            stats = StatsPrinter()
            stats.write()
            sys.exit(0)

    def _get_single_response(self, query):
        query.response = self._dispatcher.get(query.query_string + self._query_appendix)
        if query.response.status_code != 200:
            with open('errors.txt', 'a', encoding='utf-8') as f:
                f.write(str(query.response.status_code) + ':' + query.query_string + '\n')
            Stats.fails_num += 1

    def _evaluate_queries(self, queries):
        for query in queries[:]:
            analysis = self._analyzer.analyze(query)
            if analysis.killable:
                queries.remove(query)

    def _save_to_database(self, queries):
        for query in queries:
            self._mongodb.save_document(query.dictionary)

    def _slay_weak_individuals(self, score_average, number):
        if number:
            Stats.removed_num += number
            self._mongodb.remove_weak_queries(score_average, number)

    def _print_tests_num(self):
        sys.stdout.write('Generated tests: {} | Failed tests: {} \r'
                         .format(Stats.tests_num, Stats.fails_num))
        sys.stdout.flush()

    def _log_stats(self, queries):
        pass


class Selector(object):
    def __init__(self, mongodb, entities):
        self._logger = logging.getLogger(FUZZER_LOGGER)
        self._mongodb = mongodb
        self._score_average = 0
        self._passed_iterations = 0
        self._entities = entities

    @property
    def score_average(self):
        return self._score_average

    @score_average.setter
    def score_average(self, value):
        self._score_average = value

    def select(self):
        self._compute_score_average()
        if self._is_score_stagnating():
            selection = Selection(None, random.choice(list(self._entities.all())),
                                  self._score_average)
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
            if abs(old_average - current_average) < SCORE_EPS:
                return True
        return False

    def _compute_score_average(self):
        pass

    def _get_crossable(self, queryable):
        entity_set_name = queryable.entity_set.name
        parent1 = self._get_single_parent(entity_set_name, None)
        if parent1 is None:
            return None
        parent2 = self._get_single_parent(entity_set_name, ObjectId(parent1['_id']))
        if parent2 is None:
            return None
        return parent1, parent2

    def _get_single_parent(self, entity_set_name, object_id):
        queries_sample = self._mongodb.queries_sample_filter(entity_set_name, 10, object_id)
        if not queries_sample:
            return None
        parent = self._get_best_query(queries_sample)
        return parent

    def _get_best_query(self, queries_sample):
        sorted_queries = sorted(queries_sample, key=operator.itemgetter('score'), reverse=True)
        best_query = sorted_queries[0]
        self._logger.info('Selected parent is \'{}\''.format(best_query['string']))
        return best_query


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
        if not self._has_offspring_good_score(query.dictionary['predecessors'], new_score):
            return AnalysisInfo(new_score, True, self._population_score)
        return AnalysisInfo(new_score, False, self._population_score)

    def _has_offspring_good_score(self, predecessors_id, new_score):
        if predecessors_id:
            for predecessor_id in predecessors_id:
                if self._mongodb.query_by_id(predecessor_id)['score'] < new_score:
                    return True
            return False
        return True

    def _update_population_score(self, query_score):
        if self._population_score == 0:
            self._population_score = self._mongodb.overall_score()
        else:
            self._population_score += query_score


class AnalysisInfo(object):
    """A set of basic information about performed analysis."""

    def __init__(self, score, killable, population_score):
        self._score = score
        self._killable = killable
        self._population_score = population_score

    @property
    def score(self):
        return self._score

    @property
    def killable(self):
        return self._killable

    @property
    def population_score(self):
        return self._population_score


class FitnessEvaluator(object):
    """A group of heuristic functions."""

    @staticmethod
    def evaluate(query):
        total_score = 0
        keys_len = sum(len(option_name) for option_name in query.options.keys())
        query_len = len(query.query_string) - len(query.entity_name) - keys_len
        total_score += FitnessEvaluator.eval_string_length(query_len)
        total_score += FitnessEvaluator.eval_http_status_code(query.response.status_code)
        total_score += FitnessEvaluator.eval_http_response_time(query.response.elapsed
                                                                .total_seconds())
        return total_score

    @staticmethod
    def eval_http_status_code(status_code):
        if status_code == 500:
            return 100
        elif status_code == 200:
            return 0
        else:
            return -50

    @staticmethod
    def eval_http_response_time(total_seconds):
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
    pass


class Query(object):
    """A wrapper of a generated query."""

    def __init__(self, entity_name):
        self._entity_name = entity_name
        self._options = {}
        self._query_string = ''
        self._dict = None
        self._score = {}
        self._predecessors = []
        self._order = []
        self._response = None
        self._parts = 0
        self._id = ObjectId()

    @property
    def entity_name(self):
        return self._entity_name

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
        if not self._dict:
            self._create_dict()
        return self._dict

    @property
    def score(self):
        return self._score

    @property
    def query_id(self):
        return self._id

    @property
    def predecessors(self):
        return self._predecessors

    @query_string.setter
    def query_string(self, value):
        self._query_string = value

    @response.setter
    def response(self, value):
        self._response = value

    @score.setter
    def score(self, value):
        self._score = value

    def add_option(self, name, option):
        self._options[name] = option
        self._order.append('_' + name)

    def add_predecessor(self, predecessor_id):
        self._predecessors.append(predecessor_id)

    def build_string(self):
        self._query_string += self._entity_name + '?'
        for option_name in self._order:
            if option_name.endswith('filter'):
                filter_data = self._options[option_name[1:]]
                replace_forbidden_characters(filter_data['parts'])
                filter_option = FilterOption(filter_data['logicals'], filter_data['parts'],
                                             filter_data['groups'])
                option_string = FilterOptionBuilder(filter_option).build()
            else:
                option_string = self._options[option_name[1:]]
            self._query_string += option_name[1:] + '=' + option_string + '&'
        self._query_string = self._query_string.rstrip('&')

    def _create_dict(self):
        # key fields cannot start with a dollar sign in mongoDB,
        # therefore names of query options start with an underscore;
        # in the further processing, the underscore is skipped;
        # we are doing this because the search query option introduced
        # to OData 2.0 SAP applications does not contain a dollar sign
        self._dict = {
            '_id': self._id,
            'http': str(self._response.status_code),
            'error_code': getattr(self._response, 'error_code', None),
            'error_message': getattr(self._response, 'error_message', None),
            'entity_set': self._entity_name,
            'predecessors': self._predecessors,
            'string': self._query_string,
            'score': self._score,
            'order': self._order,
            '_$orderby': self._options.get(ORDERBY),
            '_$top': self._options.get(TOP),
            '_$skip': self._options.get(SKIP),
            '_$filter': self._options.get(FILTER)
        }


class Dispatcher(object):
    """A dispatcher for sending HTTP requests to the particular OData service."""

    def __init__(self, service, sap_certificate=None):
        self._logger = logging.getLogger(FUZZER_LOGGER)
        self._service = service.rstrip('/') + '/'
        self._sap_certificate = sap_certificate

        self._session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=POOL_SIZE, pool_maxsize=POOL_SIZE)
        self._session.mount(ADAPTER, adapter)
        self._session.auth = (os.getenv(ENV_USERNAME), os.getenv(ENV_PASSWORD))
        self._session.verify = self._get_sap_certificate()

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
            raise DispatcherError('An exception was raised while sending HTTP {}: {}'
                                  .format(method, requests_ex))
        self._logger.info('Received HTTP {} response from {}'.format(response.status_code, url))
        return response

    def get(self, query, **kwargs):
        return self.send('GET', query, **kwargs)

    def post(self, query, **kwargs):
        return self.send('POST', query, **kwargs)

    def _get_sap_certificate(self):
        if not self._sap_certificate:
            self_dir = os.path.dirname(__file__)
            candidate_path = os.path.join(self_dir, '../config/security/ca_sap_root_base64.crt')
            if not os.path.isfile(candidate_path):
                return None
            self._sap_certificate = candidate_path
        return self._sap_certificate


def is_filter_crossable(query1, query2):
    crossable = False
    if query1['order'] and query2['order'] == ['_$filter']:
        crossable = True
    if query1['_$filter'] and query2['_$filter'] and random.random() < FILTER_PROBABILITY:
        crossable = True
    return crossable


def build_offspring(entity_set_name, offspring):
    query = Query(entity_set_name)
    for option in offspring['order']:
        query.add_option(option[1:], offspring[option])
    return query


def replace_forbidden_characters(parts):
    for data in parts:
        if data['operand'].startswith('\''):
            data['operand'] = '\'' + replace(data['operand'][1:-1]) + '\''
        if 'params' in data:
            for index, param in enumerate(data['params']):
                if param.startswith('\''):
                    data['params'][index] = '\'' + replace(param[1:-1]) + '\''


def replace(replacing_string):
    replacing_string = replacing_string.replace('%', '%25')
    replacing_string = replacing_string.replace('&', '%26')
    replacing_string = replacing_string.replace('#', '%23')
    replacing_string = replacing_string.replace('?', '%3F')
    replacing_string = replacing_string.replace('+', '%2B')
    replacing_string = replacing_string.replace('/', '%2F')
    replacing_string = replacing_string.replace('\'', '\'\'')
    return replacing_string
