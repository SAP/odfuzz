from odfuzz.odfuzz import ResponseTimeLogger


def test_single_entity_xml_responses_count(single_entity_xml):
    count = ResponseTimeLogger().get_xml_data_count(single_entity_xml)
    assert count == 1


def test_multiple_entities_xml_response_count(multiple_entity_sets_xml):
    count = ResponseTimeLogger().get_xml_data_count(multiple_entity_sets_xml)
    assert count == 3


def test_expanded_entities_xml_response_count(expanded_entity_set_xml):
    count = ResponseTimeLogger().get_xml_data_count(expanded_entity_set_xml)
    assert count == 4


def test_no_entities_xml_response_count(no_entity_sets_xml):
    count = ResponseTimeLogger().get_xml_data_count(no_entity_sets_xml)
    assert count == 0


def test_no_entities_json_response_count(no_entity_sets_json):
    count = ResponseTimeLogger().get_json_data_count(no_entity_sets_json)
    assert count == 0


def test_single_entity_json_responses_count(single_entity_json):
    count = ResponseTimeLogger().get_json_data_count(single_entity_json)
    assert count == 1


def test_multiple_entities_json_response_count(multiple_entity_sets_json):
    count = ResponseTimeLogger().get_json_data_count(multiple_entity_sets_json)
    assert count == 3


def test_expanded_entities_json_response_count(expanded_entity_set_json):
    count = ResponseTimeLogger().get_json_data_count(expanded_entity_set_json)
    assert count == 4


def test_invalid_json_response_root_key(invalid_root_key_json):
    try:
        ResponseTimeLogger().get_json_data_count(invalid_root_key_json)
    except:
        assert False


def test_invalid_json_response_metadata_key(invalid_metadata_key_json):
    try:
        ResponseTimeLogger().get_json_data_count(invalid_metadata_key_json)
    except:
        assert False
