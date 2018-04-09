"""This module contains a builder class and wrapper classes for queryable entities"""

from pyodata.v2.model import Edmx
from pyodata.exceptions import PyODataException

from odfuzz.exceptions import BuilderError
from odfuzz.constants import CLIENT


class Builder(object):
    """A class for building and initializing all queryable entities"""

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
    def __init__(self):
        self._entities = {}

    def add(self, query_group):
        self._entities[query_group.entity_set.name] = query_group

    def get_entity(self, entity_name):
        return self._entities[entity_name]

    def all(self):
        return self._entities.values()


class QueryGroup(object):
    def __init__(self, entity_set, restrictions):
        self._entity_set = entity_set
        self._restrictions = restrictions
        self._query_options = None
        self._init_group()

    @property
    def entity_set(self):
        return self._entity_set

    @property
    def query_options(self):
        return self._query_options

    def random_options(self):
        pass

    def _init_group(self):
        pass
