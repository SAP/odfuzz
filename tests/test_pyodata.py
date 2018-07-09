def test_entity_type_parsing(schema):
    entity_types = [entity_type.name for entity_type in schema.entity_types]
    assert set(entity_types) == {'MasterEntity', 'DataEntity'}


def test_master_entity_properties_parsing(schema):
    master_entity = schema.entity_type('MasterEntity')
    master_entity_properties = [proprty.name for proprty in master_entity.proprties()]
    assert set(master_entity_properties) == {
        'DataType', 'Data', 'DataName', 'Key', 'TotalCount', 'FiscalYear', 'IsActiveEntity'}


def test_data_entity_properties_parsing(schema):
    data_entity = schema.entity_type('DataEntity')
    data_entity_properties = [proprty.name for proprty in data_entity.proprties()]
    assert set(data_entity_properties) == {'Name', 'Type', 'Value', 'Description', 'Invisible'}


def test_entity_set_parsing(schema):
    entity_sets = [entity_set.name for entity_set in schema.entity_sets]
    assert set(entity_sets) == {'DataSet', 'MasterSet'}


def test_master_set_attributes(schema):
    master_set = schema.entity_set('MasterSet')
    assert master_set.searchable
    assert master_set.addressable


def test_data_set_attributes(schema):
    data_set = schema.entity_set('DataSet')
    assert data_set.searchable
    assert not data_set.addressable


def test_master_entity_key_properties_parsing(schema):
    master_key_properties = schema.entity_type('MasterEntity').key_proprties
    assert set(key_property.name for key_property in master_key_properties) == {'Key'}


def test_data_entity_key_properties_parsing(schema):
    data_key_proprties = schema.entity_type('DataEntity').key_proprties
    assert set(key_property.name for key_property in data_key_proprties) == {'Name'}


def test_master_to_data_association_parsing(schema):
    master_to_data_association = schema.association('toDataEntity')

    association_end_roles = [end.role for end in master_to_data_association.end_roles]
    assert set(association_end_roles) == {'FromRole_toDataEntity', 'ToRole_toDataEntity'}

    association_end_entity_types = [end.entity_type.name for end in master_to_data_association.end_roles]
    assert set(association_end_entity_types) == {'MasterEntity', 'DataEntity'}


def test_master_to_master_association_parsing(schema):
    master_to_master_association = schema.association('toMasterEntity')

    association_end_roles = [end.role for end in master_to_master_association.end_roles]
    assert set(association_end_roles) == {'FromRole_toMasterEntity', 'ToRole_toMasterEntity'}

    association_end_entity_types = [end.entity_type.name for end in master_to_master_association.end_roles]
    assert set(association_end_entity_types) == {'MasterEntity', 'MasterEntity'}


def test_master_to_data_association_set_parsing(schema):
    master_to_data_association_set = schema.association_set('toDataEntitySet')

    association_set_end_roles = [end.role for end in master_to_data_association_set.ends]
    assert set(association_set_end_roles) == {'FromRole_toDataEntity', 'ToRole_toDataEntity'}

    association_set_end_entity_sets = [end.entity_set_name for end in master_to_data_association_set.ends]
    assert set(association_set_end_entity_sets) == {'MasterSet', 'DataSet'}

    entity_set_references = [end.entity_set.name for end in master_to_data_association_set.ends]
    assert set(entity_set_references) == {'MasterSet', 'DataSet'}


def test_master_to_master_association_set_parsing(schema):
    master_to_master_association_set = schema.association_set('toMasterEntitySet')

    association_set_end_roles = [end.role for end in master_to_master_association_set.ends]
    assert set(association_set_end_roles) == {'FromRole_toMasterEntity', 'ToRole_toMasterEntity'}

    association_set_end_entity_sets = [end.entity_set_name for end in master_to_master_association_set.ends]
    assert set(association_set_end_entity_sets) == {'MasterSet', 'MasterSet'}

    entity_set_references = [end.entity_set.name for end in master_to_master_association_set.ends]
    assert set(entity_set_references) == {'MasterSet', 'MasterSet'}
