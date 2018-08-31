import pytest
import unittest.mock
import odfuzz.monkey as monkey

from odfuzz.generators import RandomGenerator
from odfuzz.mutators import StringMutator, NumberMutator


def test_defined_max_length_patch(master_entity_type):
    key_property = master_entity_type.proprty('Key')
    monkey.patch_proprty_max_length(key_property)
    assert key_property.max_string_length == 5


def test_non_existent_max_length_patch(master_entity_type):
    data_type_property = master_entity_type.proprty('DataType')
    monkey.patch_proprty_max_length(data_type_property)
    assert data_type_property.max_string_length == monkey.MAX_STRING_LENGTH


def test_property_with_max_keyword_length_patch(master_entity_type):
    data_property = master_entity_type.proprty('Data')
    monkey.patch_proprty_max_length(data_property)
    assert data_property.max_string_length == monkey.MAX_STRING_LENGTH


def test_int_type_max_length_patch(master_entity_type):
    fiscal_year_property = master_entity_type.proprty('FiscalYear')
    monkey.patch_proprty_max_length(fiscal_year_property)
    with pytest.raises(AttributeError):
        assert fiscal_year_property.max_string_length == 'FAIL'


def test_string_property_generator_patch(master_entity_type):
    data_property = master_entity_type.proprty('Data')
    generator = RandomGenerator.edm_string.__get__(data_property, None)

    monkey.patch_proprty_generator(data_property)
    assert data_property.generate == generator


def test_num_property_generator_patch(master_entity_type):
    fiscal_year_property = master_entity_type.proprty('FiscalYear')
    generator = RandomGenerator.edm_int32

    monkey.patch_proprty_generator(fiscal_year_property)
    assert fiscal_year_property.generate == generator


def test_standard_property_operator_patch(master_entity_type):
    fiscal_year_property = master_entity_type.proprty('FiscalYear')
    monkey.patch_proprty_operator(fiscal_year_property)
    assert set(key for key, value in fiscal_year_property.operators.get_all()) == {'eq', 'ne', 'lt', 'le', 'gt', 'ge'}


def test_boolean_property_operator_patch(master_entity_type):
    is_active_entity_property = master_entity_type.proprty('IsActiveEntity')
    monkey.patch_proprty_operator(is_active_entity_property)
    assert set(key for key, value in is_active_entity_property.operators.get_all()) == {'eq', 'ne'}


def test_single_property_operator_patch(master_entity_type):
    single_value_property = master_entity_type.proprty('SingleValue')
    monkey.patch_proprty_operator(single_value_property)
    assert set(key for key, value in single_value_property.operators.get_all()) == {'eq'}


def test_multi_property_operator_patch(master_entity_type):
    multi_value_property = master_entity_type.proprty('MultiValue')
    monkey.patch_proprty_operator(multi_value_property)
    assert set(key for key, value in multi_value_property.operators.get_all()) == {'eq'}


def test_interval_property_operator_patch(master_entity_type):
    interval_value_property = master_entity_type.proprty('IntervalValue')
    monkey.patch_proprty_operator(interval_value_property)

    with unittest.mock.patch('random.choice', lambda x: x[0]):
        operators_names1 = set(key for key, value in interval_value_property.operators.get_all())
    with unittest.mock.patch('random.choice', lambda x: x[1]):
        operators_names2 = set(key for key, value in interval_value_property.operators.get_all())
    assert sorted((operators_names1, operators_names2), key=lambda x: len(x)) == sorted(
        ({'eq'}, {'ge', 'le'}), key=lambda x: len(x))
