"""This module contains a builder class and wrapper classes for queryable entities."""

import copy
import random

from abc import ABCMeta, abstractmethod

from pyodata.v2.model import Edmx
from pyodata.exceptions import PyODataException

from odfuzz.exceptions import BuilderError
from odfuzz.generators import RandomGenerator
from odfuzz.constants import CLIENT, GLOBAL_ENTITY, QUERY_OPTIONS, FILTER, SEARCH, TOP, SKIP


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
                               .format(self._dispatcher.service_url,
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
        entity_set = self._delete_restricted_properties(query_restr.exclude)
        is_not_restricted = self._is_not_restricted(query_restr)

        if is_not_restricted and entity_set.entity_type.proprties():
            patch_property_generators(entity_set)
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

    def _delete_restricted_properties(self, exclude_restr):
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

    def apply_restrictions(self):
        pass

    def generate(self):
        pass


def patch_property_generators(entity_set):
    for proprty in entity_set.entity_type.proprties():
        property_type = proprty.typ.name
        if property_type == 'Edm.String':
            proprty.generate = RandomGenerator.edm_string
        elif property_type == 'Edm.DateTime':
            proprty.generate = RandomGenerator.edm_datetime
        elif property_type == 'Edm.Boolean':
            proprty.generate = RandomGenerator.edm_boolean
        elif property_type == 'Edm.Byte':
            proprty.generate = RandomGenerator.edm_byte
        elif property_type == 'Edm.SByte':
            proprty.generate = RandomGenerator.edm_sbyte
        elif property_type == 'Edm.Single':
            proprty.generate = RandomGenerator.edm_single
        elif property_type == 'Edm.Guid':
            proprty.generate = RandomGenerator.edm_guid
        elif property_type == 'Edm.Decimal':
            proprty.generate = RandomGenerator.edm_decimal
        elif property_type == 'Edm.DateTimeOffset':
            proprty.generate = RandomGenerator.edm_datetimeoffset
        elif property_type == 'Edm.Time':
            proprty.generate = RandomGenerator.edm_time
        elif property_type[:7] == 'Edm.Int':
            if property_type[:2] == '16':
                proprty.generate = RandomGenerator.edm_int16
            elif property_type[:2] == '32':
                proprty.generate = RandomGenerator.edm_int32
            elif property_type[:2] == '64':
                proprty.generate = RandomGenerator.edm_int64
            else:
                proprty.generate = lambda: None
        else:
            proprty.generate = lambda: None
