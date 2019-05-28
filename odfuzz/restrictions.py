"""This module contains classes that convert restrictions to manageable objects."""

import yaml

from odfuzz.exceptions import RestrictionsError
from odfuzz.constants import EXCLUDE, INCLUDE, DRAFT_OBJECTS, QUERY_OPTIONS, FORBID_OPTION, VALUE


class RestrictionsGroup:
    """A wrapper that holds a reference for all types of restrictions."""

    def __init__(self, restrictions_file):
        self._restrictions_file = restrictions_file
        self._forbidden_options = []
        self._option_restrictions = {}

        if self._restrictions_file:
            parsed_restrictions = self._parse_restrictions()
        else:
            parsed_restrictions = {}
        self._init_restrictions(parsed_restrictions)

    def _parse_restrictions(self):
        try:
            with open(self._restrictions_file) as stream:
                restrictions_dict = yaml.safe_load(stream)
        except (EnvironmentError, yaml.YAMLError) as error:
            raise RestrictionsError('An exception was raised while parsing the restrictions file \'{}\': {}'
                                    .format(self._restrictions_file, error))
        return restrictions_dict

    def _init_restrictions(self, restrictions_dict):
        exclude_restr = restrictions_dict.get(EXCLUDE, {})
        include_restr = restrictions_dict.get(INCLUDE, {})

        for query_option in QUERY_OPTIONS:
            query_exclude_restr = exclude_restr.get(query_option, {})
            query_include_restr = include_restr.get(query_option, {})
            self._option_restrictions[query_option] = QueryRestrictions(query_exclude_restr, query_include_restr)

        self._forbidden_options = exclude_restr.get(FORBID_OPTION, [])
        self._init_draft_objects(include_restr)
        self._init_value_objects(include_restr)

    def _init_draft_objects(self, include_restr):
        restriction = QueryRestrictions({}, include_restr.get(DRAFT_OBJECTS, {}))
        self._option_restrictions[DRAFT_OBJECTS] = restriction

    def _init_value_objects(self, include_restr):
        restriction = QueryRestrictions({}, include_restr.get(VALUE, {}))
        self._option_restrictions[VALUE] = restriction

    def add_exclude_restriction(self, value, restriction_key):
        for query_restriction in self.option_restrictions():
            query_restriction.add_exclude_restriction(value, restriction_key)

    def option_restrictions(self):
        return self._option_restrictions.values()

    def forbidden_options(self):
        return self._forbidden_options

    def get(self, option_name):
        return self._option_restrictions.get(option_name)


class QueryRestrictions:
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

    def add_exclude_restriction(self, value, restriction_key):
        try:
            restrictions = self._exclude[restriction_key]
        except KeyError:
            restrictions = []
        restrictions.append(value)

        unique_values = list(set(restrictions))
        self._exclude[restriction_key] = unique_values
