"""This module contains a builder class and wrapper classes for queryable entities."""

from abc import ABCMeta, abstractmethod

from pyodata.v2.model import Edmx
from pyodata.exceptions import PyODataException

from odfuzz.exceptions import BuilderError
from odfuzz.constants import CLIENT, GLOBAL_ENTITY, QUERY_OPTIONS, FILTER, SEARCH, TOP, SKIP


class Builder(object):
    """A class for building and initializing all queryable entities."""

    def __init__(self, dispatcher, restrictions):
        self._restrictions = restrictions
        self._dispatcher = dispatcher
        self._queryable = QueryableEntities()

    @property
    def queryable(self):
        return self._queryable

    def build(self):
        data_model = self._get_data_model()
        for entity_set in data_model.entity_sets:
            query_group = QueryGroup(entity_set, self._restrictions)
            self._queryable.add(query_group)

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
        self._init_group()

    @property
    def entity_set(self):
        return self._entity_set

    def query_options(self):
        return self._query_options.values()

    def query_option(self, query_name):
        return self._query_options[query_name]

    def random_options(self):
        pass

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

    def _init_filter_query(self):
        query_restr = self._restrictions.restriction(FILTER)
        is_filterable = self._is_entity_filterable(query_restr.exclude)
        is_not_restricted = self._is_not_restricted(query_restr)

        if is_filterable and is_not_restricted:
            self._query_options[FILTER] = FilterQuery(self._entity_set, query_restr)

    def _is_not_restricted(self, exclude_restr):
        restricted_entities = getattr(exclude_restr, GLOBAL_ENTITY, None)

        if restricted_entities:
            if self._entity_set.name in restricted_entities:
                return False
        return True

    def _is_entity_filterable(self, exclude_restr):
        restr_proprty_list = exclude_restr.get(self._entity_set.name, [])

        for proprty in self._entity_set.entity_type.proprties():
            if proprty in restr_proprty_list:
                continue
            if proprty.filterable:
                return True
        return False


class QueryOption(metaclass=ABCMeta):
    """An abstract class for a query option."""

    def __init__(self, entity_set, restrictions=None):
        self._entity_set = entity_set
        self._restrictions = restrictions

    @property
    def entity(self):
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
