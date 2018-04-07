"""This module contains a builder class and wrapper classes for queryable entities"""

from pyodata.v2.model import Edmx
from pyodata.exceptions import PyODataException

from odfuzz.exceptions import BuilderError
from odfuzz.constants import CLIENT


class Builder(object):
    """A class for building and initializing all queryable entities"""

    def __init__(self, restrictions, dispatcher):
        self._restrictions = restrictions
        self._dispatcher = dispatcher
        self._queryable = None

    @property
    def queryable(self):
        return self._queryable

    def build(self):
        data_model = self._get_data_model()

    def _get_data_model(self):
        metadata_response = self._get_metadata_from_service()
        try:
            service_model = Edmx.parse(metadata_response.content)
        except PyODataException as pyodata_ex:
            raise BuilderError('An exception occurred while parsing metadata: {}'
                               .format(str(pyodata_ex)))
        return service_model

    def _get_metadata_from_service(self):
        metadata_request = '$metadata?' + CLIENT
        try:
            metadata_response = self._dispatcher.get(metadata_request)
        except Exception as ex:
            raise BuilderError('An exception occurred while retrieving metadata: {}'
                               .format(str(ex)))
        if metadata_response.status_code != 200:
            raise BuilderError('Cannot retrieve metadata from {}. Status code is {}'
                               .format(self._dispatcher.service_url,
                                       metadata_response.status_code))
        return metadata_response
