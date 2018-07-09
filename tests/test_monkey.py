import pytest
import random
import odfuzz.monkey as monkey

from odfuzz.generators import RandomGenerator, StringMutator, NumberMutator


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


def test_string_property_mutator_patch(master_entity_type):
    data_type_property = master_entity_type.proprty('DataType')
    string_mutators = [func_name for func_name in StringMutator.__dict__.keys() if not func_name.startswith('_')]

    monkey.patch_proprty_mutator(data_type_property)
    data_type_mutators = [func_name for func_name in data_type_property.__dict__.keys() if func_name in string_mutators]
    assert set(data_type_mutators) == set(string_mutators)
    assert data_type_property.mutate


def test_num_property_mutator_patch(master_entity_type):
    total_count_property = master_entity_type.proprty('TotalCount')
    number_mutators = [func_name for func_name in NumberMutator.__dict__.keys() if not func_name.startswith('_')]

    monkey.patch_proprty_mutator(total_count_property)
    total_count_mutators = [func_name for func_name in total_count_property.__dict__.keys()
                            if func_name in number_mutators]
    assert set(total_count_mutators) == set(number_mutators)
    assert total_count_property.mutate


def test_standard_property_operator_patch(master_entity_type):
    fiscal_year_property = master_entity_type.proprty('FiscalYear')
    monkey.patch_proprty_operator(fiscal_year_property)
    assert set(fiscal_year_property.operators.keys()) == {'eq', 'ne', 'lt', 'le', 'gt', 'ge'}


def test_boolean_property_operator_patch(master_entity_type):
    is_active_entity_property = master_entity_type.proprty('IsActiveEntity')
    monkey.patch_proprty_operator(is_active_entity_property)
    assert set(is_active_entity_property.operators.keys()) == {'eq', 'ne'}
