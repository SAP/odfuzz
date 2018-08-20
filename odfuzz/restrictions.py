"""This module contains classes that convert restrictions to manageable objects."""

import yaml

from odfuzz.exceptions import RestrictionsError
from odfuzz.constants import EXCLUDE, INCLUDE, DRAFT_OBJECTS, QUERY_OPTIONS


class RestrictionsGroup(object):
    """A wrapper that holds a reference for all types of restrictions."""

    def __init__(self, restrictions_file):
        self._restrictions_file = restrictions_file
        self._draft = {}
        self._restrictions = {}
        self._parse_restrictions()

    def restrictions(self):
        return self._restrictions.values()

    def restriction(self, query_name):
        return self._restrictions[query_name]

    def _parse_restrictions(self):
        try:
            with open(self._restrictions_file) as stream:
                restrictions_dict = yaml.safe_load(stream)
        except (EnvironmentError, yaml.YAMLError) as error:
            raise RestrictionsError('An exception was raised while parsing the restrictions file \'{}\': {}'
                                    .format(self._restrictions_file, error))
        self._init_restrictions(restrictions_dict)

    def _init_restrictions(self, restrictions_dict):
        exclude_restr = restrictions_dict.get(EXCLUDE, None)
        include_restr = restrictions_dict.get(INCLUDE, None)

        for query_option in QUERY_OPTIONS:
            query_exclude_restr = None
            query_include_restr = None
            if exclude_restr:
                query_exclude_restr = exclude_restr.get(query_option, None)
            if include_restr:
                query_include_restr = include_restr.get(query_option, None)

            self._restrictions[query_option] = QueryRestrictions(
                query_exclude_restr, query_include_restr
            )

        self._init_draft_objects(include_restr)

    def _init_draft_objects(self, include_restr):
        if include_restr:
            self._restrictions[DRAFT_OBJECTS] = include_restr.get(DRAFT_OBJECTS, {})


class QueryRestrictions(object):
    """A set of restrictions applied to a query option."""

    def __init__(self, exclude_restr, include_restr):
        self._exclude = exclude_restr
        self._include = include_restr

    @property
    def include(self):
        return self._include

    @property
    def exclude(self):
        return self._exclude
