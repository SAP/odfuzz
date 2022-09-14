"""This module contains core parts of the fuzzer and additional handler classes."""

import random
import hashlib
import json

from copy import deepcopy
from collections import namedtuple

from odfuzz.entities import FilterOptionBuilder, FilterOption, \
    OrderbyOptionBuilder, OrderbyOption
from odfuzz.config import Config

# pylint: disable=wildcard-import
from odfuzz.constants import *  

class Queryable:
    """ Assemble the final query by appending different enttity parts.
    """

    SelfMock = namedtuple('SelfMock', 'max_length')

    def __init__(self, queryable, logger, async_requests_num):
        self._queryable = queryable

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


class SingleQueryable(Queryable):
    """
    used when fuzzer is not triggered with async option, generates URLs by one
    """
    def generate(self):
        query,body = self.generate_query()
        body = json.dumps(body)
        return [query,body]

class Query:
    """A wrapper of a generated query."""

    def __init__(self, accessible_entity):
        self._accessible_entity = accessible_entity
        self._options = {}
        self._query_string = ''
        self._dict = None
        self._order = []
        self._response = None
        self._parts = 0
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
    def query_id(self):
        return self._id

    @property
    def options_strings(self):
        return self._options_strings

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

    '''
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
    '''

    def _add_appendix(self):
        if Config.fuzzer.sap_client:
            self._query_string += '&' + 'sap-client=' + Config.fuzzer.sap_client
        if Config.fuzzer.data_format and (Config.fuzzer.http_method_enabled == "GET"):
            self._query_string += '&' + '$format=' + Config.fuzzer.data_format


class HashGenerator:
    @staticmethod
    def generate(string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()


class NullObject:
    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, item):
        return self

# following methods were part of Queryable, Query and Fuzzer class, moved out simply because of self. warning logically are part of Queryable
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