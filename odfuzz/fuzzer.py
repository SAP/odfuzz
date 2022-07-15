"""This module contains core parts of the fuzzer and additional handler classes."""

import random
import io
import sys
import hashlib
import logging
import gevent
import requests
import requests.adapters
import json

from copy import deepcopy
from collections import namedtuple
from abc import ABCMeta, abstractmethod
from lxml import etree
from gevent.pool import Pool
from bson.objectid import ObjectId
from pymongo.errors import ServerSelectionTimeoutError  #TODO leaky abstraction, should be new exception class in database.py, untied to specific database usage.

from odfuzz.entities import DispatchedBuilder, FilterOptionBuilder, FilterOptionDeleter, FilterOption, \
    OrderbyOptionBuilder, OrderbyOption, KeyValuesBuilder
from odfuzz.restrictions import RestrictionsGroup
from odfuzz.databases import MongoDB, MongoDBHandler
from odfuzz.exceptions import DispatcherError
from odfuzz.config import Config
from odfuzz.utils import decode_string
from odfuzz import __version__

# pylint: disable=wildcard-import
from odfuzz.constants import *  


class Manager:
    """A class for managing the fuzzer runtime."""

    def __init__(self, bind, arguments, collection_name):
        Config.init()

        self._dispatcher = Dispatcher(arguments)
        self._asynchronous = arguments.asynchronous
        self._first_touch = arguments.first_touch
        self._restrictions = RestrictionsGroup(arguments.restrictions)
        self._collection_name = collection_name
        self._logger = logging.getLogger(FUZZER_LOGGER)
        
        self._using_encoder = Config.fuzzer.use_encoder

    def start(self):
        self._logger.info('odfuzz version: ' + __version__)

        seed = Config.fuzzer.cli_runner_seed
        random.seed(seed, version=1)
        self._logger.info('random.seed() is set to \'{}\''.format(seed))

        database = self.establish_database_connection(MongoDBHandler, MongoDB)
        entities = self.build_entities()
        fuzzer = Fuzzer(self._dispatcher, entities, database, self._asynchronous,
                        self._using_encoder)

        fuzzer.run()

    def establish_database_connection(self, database_handler, database_client):
        self._logger.info('Connecting to the database - Collection: {}'.format(self._collection_name))
        try:
            return database_handler(database_client(self._collection_name))
        except ServerSelectionTimeoutError:
            sys.exit(1)

    def build_entities(self):
        """ Performs the first HTTP request of fuzzer to target server for $metadata and generates queryable entities for further fuzzing.

        """
        builder = DispatchedBuilder(self._dispatcher, self._restrictions, self._first_touch)
        return builder.build()
        # TODO: possible feature/enhancement.. only generate metadata calls and save them or requests X URLS without evolution algorithm (REST service)


class Fuzzer:
    """A main class that is responsible for the fuzzing process."""

    def __init__(self, dispatcher, entities, database, asynchronous, using_encoder):
        self._logger = logging.getLogger(FUZZER_LOGGER)
        self._urls_logger = URLsLogger()
        self._dispatcher = dispatcher
        self._entities = entities
        self._database = database

        self._analyzer = Analyzer(database)
        self._selector = Selector(database, entities)

        self._asynchronous = asynchronous
        if asynchronous:
            self._queryable_factory = MultipleQueryable
            self._dispatch = self._get_multiple_responses
        else:
            self._queryable_factory = SingleQueryable
            self._dispatch = self._get_single_response

        if not using_encoder:
            self._decode_queries = lambda *args: None

        # This step is required to redirect printing of stack trace by greenlets. I haven't
        # found any other conventional way to suppress such a printing. In the past, it was
        # possible  to set which type of exceptions shouldn't be printed by:
        # gevent.hub.Hub.NOT_ERROR=(Exception,)
        # Source: https://github.com/gevent/gevent/issues/55
        #
        # If anybody in the future will want to print output to the standard error output,
        # he/she will be required to set sys.stderr back to its default value by:
        # sys.stderr = sys.__stderr__
        # Source: https://docs.python.org/3/library/sys.html#sys.__stderr__
        sys.stderr = LoggerErrorWritter(self._logger)

    def run(self):

        self._database.delete_collection()
        self.seed_population()
        if self._database.total_entries() == 0:
            self._logger.info('There are no queries generated yet.')
            sys.stdout.write('OData service does not contain any queryable entities. Exiting...\n')
            sys.exit(0)

        self._selector.score_average = self._database.total_score() / self._database.total_entries()
        self.evolve_population()

    def seed_population(self):
        """
        Initial and first half of the fuzzing process.

        Parses the $metadata from the server and generates URLs for *all* entities present (random values).

        After finishing, we have touched each entity and it is time to employ the genetic sampling
        for better probability of hitting the server errors.

        See: https://github.wdf.sap.corp/ODfuzz/ODfuzz/blob/doc_architecture/doc/architecture.rst#query-groups
        See: https://github.wdf.sap.corp/ODfuzz/ODfuzz/blob/doc_architecture/doc/restrictions.rst

        :return:
        """
        self._logger.info('Seeding population with requests...')
        for queryable in self._entities.all():
            entityset_urls_count = len(queryable.entity_set.entity_type.proprties()) * Config.fuzzer.urls_per_property
            if self._asynchronous:
                entityset_urls_count = round(entityset_urls_count / Config.dispatcher.async_requests_num)
            self._logger.info('Population range for entity \'{}\' is set to {}'
                              .format(queryable.entity_set.name, entityset_urls_count))
            for _ in range(entityset_urls_count):
                q = self._queryable_factory(queryable, self._logger, Config.dispatcher.async_requests_num)
                queries = q.generate()
                self._send_queries(queries)
                self._analyze_queries(queries)
                self._save_queries(queries)

    def evolve_population(self):
        """

        :return:
        """
        self._logger.info('Evolving population of requests...')
        while True:
            selection = self._selector.select()
            if selection.crossable:
                self._logger.info('Crossing parents...')
                q = self._queryable_factory(selection.queryable, self._logger, Config.dispatcher.async_requests_num)
                queries = q.crossover(selection.crossable)
                self._send_queries(queries)
                analyzed_queries = self._analyze_queries(queries)
                self._remove_weak_queries(analyzed_queries, queries)
            else:
                self._logger.info('Generating new queries...')
                q = self._queryable_factory(selection.queryable, self._logger, Config.dispatcher.async_requests_num)
                queries = q.generate()
                self._send_queries(queries)
                self._analyze_queries(queries)
                self._slay_weakest_individuals(len(queries))
            self._save_queries(queries)

    def _save_queries(self, queries):
        self._decode_queries(queries)
        self._urls_logger.log_ursl(queries)
        self._save_to_database(queries)

    def _decode_queries(self, queries):
        for query in queries:
            self._decode_single_query(query)

    def _decode_single_query(self, query):
        self._decode_filter_option(query[0])
        self._decode_search_option(query[0])
        self._decode_accessible_keys(query[0])

    def _decode_filter_option(self, query):
        filter_option = query.dictionary.get('_$filter')
        if filter_option:
            for part in filter_option['parts']:
                # decode all Edm types, even those which were not encoded
                decoded_value = decode_string(part['operand'])
                part['operand'] = decoded_value

                # decode functions' parameters
                params = part.get('params', None)
                if params:
                    for i, param in enumerate(params):
                        params[i] = decode_string(param)

    def _decode_search_option(self, query):
        search_option = query.dictionary.get('_search')
        if search_option:
            decoded_value = decode_string(search_option)
            query.dictionary['_search'] = decoded_value

    def _decode_accessible_keys(self, query):
        """Decode accessible keys that identify a single entity within an entity set.

        For example: Customers(CustomerID='%C3%AF%C2%B6') -> Customers(CustomerID='ï¶')
        """
        accessible_keys = query.dictionary.get('accessible_keys', None)
        if accessible_keys:
            for key, value in accessible_keys.items():
                accessible_keys[key] = decode_string(value)

    def _send_queries(self, queries):
        while True:
            success = self._dispatch(queries)
            if success:
                break

    def _get_multiple_responses(self, queries):
        pool = Pool(Config.dispatcher.async_requests_num)
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
        try:
            self._get_response(queries)
        except DispatcherError:
            self._handle_dispatcher_exception()
            return False
        return True

    def _get_response(self, query):
        query[0].response = self._dispatcher.get(query[0].query_string, timeout=REQUEST_TIMEOUT)
        if query[0].response.status_code != 200:
            self._set_error_attributes(query)
        else:
            self._response_logger.log_response_time_and_data(query[0], Config.fuzzer.data_format)
            setattr(query[0].response, 'error_code', '')
            setattr(query[0].response, 'error_message', '')

    def _handle_dispatcher_exception(self):
        self._logger.info('Retrying in {} seconds...'.format(RETRY_TIMEOUT))
        gevent.sleep(RETRY_TIMEOUT)

    def _analyze_queries(self, queries):
        analyzed_offsprings = []
        for query in queries:
            analyzed_offsprings.append(self._analyzer.analyze(query))
        return analyzed_offsprings

    def _remove_weak_queries(self, analyzed_offsprings, queries):
        for offspring in analyzed_offsprings:
            offspring.slay_weak_individual(queries)

    def _slay_weakest_individuals(self, number_of_individuals):
        self._database.delete_worst_entries(number_of_individuals)

    def _save_to_database(self, queries):
        for query in queries:
            self._database.save_entry(query[0].dictionary)

    def _set_error_attributes(self, query):
        self._set_attribute_value(query, 'error_code', 'error', 'code')
        self._set_attribute_value(query, 'error_message', 'error', 'message')

    def _set_attribute_value(self, query, attr, *args):
        try:
            json = query[0].response.json()
            value = self._get_attr_from_json(json, *args)
        except ValueError:
            value = self._get_attr_from_xml(query[0].response.content, *args)
        setattr(query[0].response, attr, value)

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


class Queryable:
    """ Assemble the final query by appending different entitity parts.
    """

    SelfMock = namedtuple('SelfMock', 'max_length')

    def __init__(self, queryable, logger, async_requests_num):
        self._queryable = queryable
        self._logger = logger
        self._async_requests_num = async_requests_num

    def generate_query(self):
        accessible_entity, body_key_pairs = self._queryable.get_accessible_entity()
        query = Query(accessible_entity)
        self.generate_options(query)
        body = self.generate_body(accessible_entity, body_key_pairs)
        return query,body
    
    def generate_put_post_body(self, accessible_entity, body_key_pairs):
        body={}
        properties = accessible_entity.entity_set.entity_type._properties
        for prprty in properties.values():
            #checking if the property exists in generated body_key_pairs. If yes, then the body equivalent value is used
            if prprty.name in body_key_pairs:
                generated_body = body_key_pairs[prprty.name]
            else:
                generated_body = prprty.generate(generator_format='body')
            try:
                generated_body = generated_body.strip("\'")
            except:
                pass
            body[prprty._name] = generated_body
        return body


    def generate_merge_body(self, accessible_entity, body_key_pairs):
        body = {}
        properties = {}
        #if the property is a key, then its omitted from the body
        for proprty in accessible_entity.entity_set.entity_type._properties:
            if proprty not in body_key_pairs:
                properties[proprty] = accessible_entity.entity_set.entity_type._properties[proprty]
        #if no non-key properties exist, then empty body returned
        if len(properties) == 0:
            return properties
        #The length of the body is randomly choosen, between 1 and the number of non-key properties
        property_count = random.randint(1,len(properties))
        #The body is populated with properties selected at random
        for i in range(0,property_count):
            selected_property = random.choice(list(properties.values()))
            generated_body = selected_property.generate(generator_format='body')
            try:
                generated_body = generated_body.strip("\'")
            except:
                pass
            body[selected_property._name] = generated_body
            #property removed from the properties dict to avoid creating duplicates
            properties.pop(selected_property._name)
        return body
        

    def generate_body(self,accessible_entity,body_key_pairs):
        #body initialised as empty dict. For GET and DELETE the body would remain empty
        body={}
        if Config.fuzzer.http_method_enabled == "PUT" or Config.fuzzer.http_method_enabled == "POST":
            body = self.generate_put_post_body(accessible_entity, body_key_pairs)
        elif Config.fuzzer.http_method_enabled == "MERGE":
            body = self.generate_merge_body(accessible_entity, body_key_pairs)
        elif Config.fuzzer.http_method_enabled == "GET" or Config.fuzzer.http_method_enabled == "DELETE":
            pass
        else:
            raise ValueError("Config.fuzzer.http_method_enabled has unknown value")
        return body

    def generate_options(self, query):
        depending_data = {}
        for option in self._queryable.random_options():
            generated_option = option.generate(depending_data)
            query.add_option(option.name, generated_option.data)
            depending_data[option.name] = option.get_depending_data()
            #for $skip and $top; one parameter contextually depends on another and the value of top+skip must be lower than MAX(INT)
        query.build_string()
        self._logger.info('Generated query \'{}\''.format(query.query_string))

class MultipleQueryable(Queryable):
    """ Used when fuzzer triggered with async option, generates URL for requests in async batches
    TODO refactor rename, so its not mistaken with QueryGroups.. this is about something different,
    Query is the part of URL, QueryGroups is that urls are structurally different, this is about
    possible name...   SendableQueryBatch for this async and SingleQueryable => SendableQuery
    """
    def generate(self):
        queries = []
        for _ in range(self._async_requests_num):
            query = self.generate_query()
            if query:
                queries.append(query)
        return queries

    def crossover(self, crossable_selection):
        children = []
        for _ in range(self._async_requests_num):
            accessible_keys = crossable_selection[0].get('accessible_keys', None)
            if accessible_keys and random.random() <= KEY_VALUES_MUTATION_PROB:
                query = self.build_mutated_accessible_keys(accessible_keys, crossable_selection[0])
                children.append(query)
            else:
                query1, query2 = crossable_selection
                offspring = self._crossover_queries(query1, query2)
                if offspring:
                    children.append(offspring)
        return children


class SingleQueryable(Queryable):
    """
    used when fuzzer is not triggered with async option, generates URLs  by one
    """
    def generate(self):
        query,body = self.generate_query()
        body = json.dumps(body)
        return [query,body]

    def crossover(self, crossable_selection):
        query1, query2 = crossable_selection
        accessible_keys = crossable_selection[0].get('accessible_keys', None)
        if accessible_keys and random.random() <= KEY_VALUES_MUTATION_PROB:
            query = self.build_mutated_accessible_keys(accessible_keys, crossable_selection[0])
        else:
            query = self._crossover_queries(query1, query2)
        return [query]


class URLsLogger:
    def __init__(self):
        self._urls_logger = logging.getLogger(URLS_LOGGER)

    def log_ursl(self, queries):
        for query in queries:
            self._urls_logger.info(query[0].url_hash + ':' + query[0].query_string)

class Selector:
    """
    used in genetic loop,
    see https://github.wdf.sap.corp/ODfuzz/ODfuzz/blob/doc_architecture/doc/architecture.rst#selector
    """
    def __init__(self, database, entities):
        self._logger = logging.getLogger(FUZZER_LOGGER)
        self._database = database
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
        if self._is_score_stagnating():
            selection = Selection(None, random.choice(list(self._entities.all())))
        else:
            selection = self._crossable_selection()
        self._passed_iterations += 1

        return selection

    def _crossable_selection(self):
        queryable = random.choice(list(self._entities.all()))
        crossable = self._get_crossable(queryable)
        selection = Selection(crossable, queryable)
        return selection

    def _is_score_stagnating(self):
        if self._passed_iterations > ITERATIONS_THRESHOLD:
            self._passed_iterations = 0
            current_average = self._database.total_score() / self._database.total_entries()
            old_average = self._score_average
            self._score_average = current_average
            if (current_average - old_average) < SCORE_EPS:
                return True
        return False

    def _get_crossable(self, queryable):
        entity_set_name = queryable.entity_set.name
        parent1 = self._database.sample_filter_entry(entity_set_name, None)
        if parent1 is None:
            return None
        parent2 = self._database.sample_filter_entry(entity_set_name, ObjectId(parent1['_id']))
        if parent2 is None:
            return None
        return parent1, parent2


class Selection:
    """A container that holds objects created by Selector."""

    def __init__(self, crossable, queryable):
        self._crossable = crossable
        self._queryable = queryable

    @property
    def crossable(self):
        return self._crossable

    @property
    def queryable(self):
        return self._queryable


class Analyzer:
    """Fitness function evaluator for analyzing responses from generated queries.

    Higher score propagates further in the genetic algorithm.
    """

    def __init__(self, database):
        self._database = database
        self._population_score = 0

    def analyze(self, query):
        new_score = FitnessEvaluator.evaluate(query)
        query[0].score = new_score
        self._update_population_score(new_score)
        predecessors_ids = query[0].dictionary['predecessors']
        if predecessors_ids:
            offspring = self._build_offspring_by_score(predecessors_ids, query[0], new_score)
        else:
            offspring = EmptyOffspring(self._database)
        return offspring

    def _build_offspring_by_score(self, predecessors_id, query, new_score):
        for predecessor_id in predecessors_id:
            if self._database.find_entry(predecessor_id)['score'] < new_score:
                return BetterOffspring(self._database, predecessor_id)
        return WorseOffspring(query)

    def _update_population_score(self, query_score):
        if self._population_score == 0:
            self._population_score = self._database.total_score()
        else:
            self._population_score += query_score


class Offspring(metaclass=ABCMeta):
    """
        In mutation,
    """
    def __init__(self, database):
        self._database = database

    @abstractmethod
    def slay_weak_individual(self, queries):
        pass

    @abstractmethod
    def get_number_of_slayed(self):
        pass


class BetterOffspring(Offspring):
    def __init__(self, database, worse_predecessor_id):
        super(BetterOffspring, self).__init__(database)
        self._worse_predecessor_id = worse_predecessor_id
        self._slayed = 0

    def slay_weak_individual(self,queries):
        deleted_num = self._database.delete_entry(self._worse_predecessor_id)
        if deleted_num == 0:
            self._database.delete_worst_entries(1)
        self._slayed = 1

    def get_number_of_slayed(self):
        return self._slayed


class WorseOffspring(Offspring):
    def __init__(self, offspring):
        self._offspring = offspring
        self._slayed = 0

    def slay_weak_individual(self, queries):
        queries.remove(self._offspring)
        self._slayed = 1

    def get_number_of_slayed(self):
        return self._slayed


class EmptyOffspring(Offspring):
    def slay_weak_individual(self, queries):
        self._database.delete_worst_entries(1)

    def get_number_of_slayed(self):
        return 1


class FitnessEvaluator:
    """A group of heuristic functions.

    It is preffering shorther URLs for HTTP 500 responses and ignores other HTTP status codes.
    It preffers URLs where smaller response content took significantly longer time (i.e. empiric observation of server handling bad requests).
    """

    @staticmethod
    def evaluate(query):
        total_score = 0
        keys_len = sum(len(option_name) for option_name in query[0].options.keys())
        query_len = len(query[0].query_string) - len(query[0].entity_name) - keys_len
        total_score += FitnessEvaluator.eval_string_length(query_len)
        total_score += FitnessEvaluator.eval_http_status_code(
            query[0].response.status_code, query[0].response.error_code, query[0].response.error_message)
        total_score += FitnessEvaluator.eval_http_response_time(query[0].response)
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


class SAPErrors:
    """A container of all types of errors produced by the SAP systems."""
    #TODO this is hardcoded for expected usage of ODfuzz against SAP systems; would not work correctly against generic Odata service
    @staticmethod
    def evaluate(error_code, error_message):
        # TODO: handle more types of the SY/530 error, e.g. "XYZ is not created in language", "XYZ not in system", ...
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


class Query:
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
                                 'search': '', '$inlinecount': ''}
        self._url_hash = ''

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

    @property
    def url_hash(self):
        return self._url_hash

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
    #TODO refactor rename build_url_part - this creates the parts after /Entity?$filter... etc ; not entire URL to send to Dispatcher.
        self._query_string = self._accessible_entity.path + '?'
        if Config.fuzzer.http_method_enabled == "GET":
            for option_name in self._order:
                if option_name.endswith('filter'):
                    filter_data = deepcopy(self._options[option_name[1:]])
                    option_string = build_filter_string(filter_data)
                elif option_name.endswith('orderby'):
                    orderby_data = self._options[option_name[1:]]
                    orderby_option = OrderbyOption(orderby_data)
                    option_string = OrderbyOptionBuilder(orderby_option).build()
                elif option_name.endswith('expand'):
                    option_string = ','.join(self._options[option_name[1:]])
                else:
                    option_string = self._options[option_name[1:]]
                self._options_strings[option_name[1:]] = option_string
                self._query_string += option_name[1:] + '=' + option_string + '&'
        self._query_string = self._query_string.rstrip('&')
        self._add_appendix()
        self._query_string = self._query_string.replace("?&","?")

        self._url_hash = HashGenerator.generate(self._query_string)

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
            '_search': self._options.get(SEARCH),
            '_$inlinecount': self._options.get(INLINECOUNT)
        }

    def _add_appendix(self):
        if Config.fuzzer.sap_client:
            self._query_string += '&' + 'sap-client=' + Config.fuzzer.sap_client
        if Config.fuzzer.data_format and (Config.fuzzer.http_method_enabled == "GET"):
            self._query_string += '&' + '$format=' + Config.fuzzer.data_format


class HashGenerator:
    @staticmethod
    def generate(string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()


class Dispatcher:
    """A dispatcher for sending HTTP requests to the particular OData service."""

    def __init__(self, arguments):
        self._config = Config.dispatcher

        self._logger = logging.getLogger(FUZZER_LOGGER)
        self._service = arguments.service.rstrip('/') + '/'

        self._session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=self._config.async_requests_num,
                                                pool_maxsize=self._config.async_requests_num)
        self._session.mount(ACCESS_PROTOCOL, adapter)
        self._session.verify = self._get_sap_certificate()
        self._session.headers.update({'user-agent': 'odfuzz/1.0'})

        self._init_auth_credentials(arguments.credentials)

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
        if self._config.has_certificate:
            candidate_path = self._config.cert_file_path
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
    """ """
    def __init__(self, logger):
        self._logger = logger

    def write(self, message):
        self._logger.error(message)


class NullObject:
    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, item):
        return self

# following methods were part of Queryable, Query and Fuzzer class, moved out simply because of self. warning logically are part of Queryable
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


def build_xpath_format_string(*args):
    xpath_string = ''
    for arg in args:
        xpath_string += '/m:{}'.format(arg)
    xpath_string += '/text()'
    return xpath_string


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
