"""This module contains core parts of the fuzzer and additional handler classes."""

import random
import time
import os
import sys
import requests
import pymongo

from gevent.pool import Pool

from odfuzz.entities import Builder, FilterOptionBuilder
from odfuzz.restrictions import RestrictionsGroup
from odfuzz.exceptions import DispatcherError
from odfuzz.constants import ENV_USERNAME, ENV_PASSWORD, MONGODB_NAME, SEED_POPULATION, \
    MONGODB_COLLECTION, FILTER, POOL_SIZE


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
        self._dispatcher = dispatcher
        self._entities = entities
        self._mongodb = MongoClient()
        self._analyzer = Analyzer()
        self._selector = Selector()

        self._async = kwargs.get('async')
        if self._async:
            self._generate = self._generate_multiple
        else:
            self._generate = self._generate_single

        self._tests_num = 0
        self._fails_num = 0

    def run(self):
        time_seed = time.time()
        random.seed(time_seed)

        self.seed_population()
        self.evolve_population()

    def seed_population(self):
        for queryable in self._entities.all():
            seed_range = len(queryable.entity_set.entity_type.proprties()) * SEED_POPULATION
            if self._async:
                seed_range = round(seed_range / POOL_SIZE)
            for _ in range(seed_range):
                queries = self._generate(queryable)
                self._evaluate_queries(queries)
                self._save_to_database(queries)
                self._print_tests_num()

    def evolve_population(self):
        pass

    def _generate_multiple(self, queryable):
        queries = []
        for _ in range(POOL_SIZE):
            query = self._generate_query(queryable)
            if query:
                queries.append(query)
                self._tests_num += 1
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
        try:
            option = queryable.query_option(FILTER)
        except KeyError:
            return None

        generated_option = option.generate()
        query.add_option(FILTER, generated_option.data)
        query.query_string = query.entity_name + '?' + option.name \
                                               + '=' + generated_option.option_string
        return query

    def _get_multiple_responses(self, queries):
        responses = []
        pool = Pool(POOL_SIZE)
        for query in queries:
            responses.append(pool.spawn(self._get_single_response, query))
        pool.join()

    def _get_single_response(self, query):
        query.response = self._dispatcher.get(query.query_string)
        if query.response.status_code != 200:
            self._fails_num += 1

    def _evaluate_queries(self, queries):
        for query in queries:
            self._analyzer.analyze(query)

    def _save_to_database(self, queries):
        for query in queries:
            self._mongodb.save_document(query.dictionary)

    def _print_tests_num(self):
        sys.stdout.write('Generated tests: {} | Failed tests: {} \r'
                         .format(self._tests_num, self._fails_num))
        sys.stdout.flush()


class Selector(object):
    def __init__(self):
        pass

    def select(self):
        pass


class Analyzer(object):
    def __init__(self):
        pass

    def analyze(self, query):
        pass


class Heuristics(object):
    pass


class SAPErrors(object):
    """A container of all types of errors produced by the SAP systems."""
    pass


class Query(object):
    """A wrapper of a generated query."""

    def __init__(self, entity_name):
        self._entity_name = entity_name
        self._options = {}
        self._query_string = ''
        self._dict = {}
        self._score = {}
        self._response = None

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

    def _create_dict(self):
        self._dict['HTTP'] = str(self._response.status_code)
        self._dict['ErrorCode'] = getattr(self._response, 'error_code', None)
        self._dict['ErrorMessage'] = getattr(self._response, 'error_message', None)
        self._dict['EntitySet'] = {'name': self._entity_name,
                                   'queries': [
                                       {'string': self._query_string,
                                        'score': self._score,
                                        'search': self._options.get('search'),
                                        'top': self._options.get('$top'),
                                        'skip': self._options.get('$skip'),
                                        'filter': self._options.get(FILTER)}
                                   ]}


class MongoClient(object):
    """A NoSQL database client."""

    def __init__(self):
        self._mongodb = pymongo.MongoClient()
        self._collection = self._mongodb[MONGODB_NAME][MONGODB_COLLECTION]

    def save_document(self, query_dict):
        was_inserted = self.insert_single_document(query_dict)
        if not was_inserted:
            self.update_single_document(query_dict)

    def insert_single_document(self, query_dict):
        cursor = self._collection.find({'EntitySet.name': query_dict['EntitySet']['name'],
                                        'ErrorCode': query_dict['ErrorCode']})
        if cursor.count() == 0:
            self._collection.insert_one(query_dict)
            return True
        return False

    def update_single_document(self, query_dict):
        entity_set_dict = query_dict['EntitySet']
        query = entity_set_dict['queries'][0]
        self._collection.update_one(
            {'$and': [
                {'EntitySet.name': entity_set_dict['name']},
                {'ErrorCode': query_dict['ErrorCode']},
                {'EntitySet.queries.string': {'$ne': query['string']}}
            ]},
            {'$push': {'EntitySet.queries': query}}
        )


class Dispatcher(object):
    """A dispatcher for sending HTTP requests to the particular OData service."""

    def __init__(self, service, sap_certificate=None):
        self._service = service.rstrip('/') + '/'
        self._sap_certificate = sap_certificate

        self._session = requests.Session()
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
