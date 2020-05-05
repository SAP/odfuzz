import pytest

from bson import ObjectId
from mongomock import MongoClient

from odfuzz.databases import MongoDBHandler


class MongoDBMock:
    def __init__(self):
        self._collection = MongoClient()['db']['collection']
    
    @property
    def collection(self):
        return self._collection


def test_database_insert_one(data_three_filter_logicals_company_code):
    mongo_mock = MongoDBMock()
    mongo_handler = MongoDBHandler(mongo_mock)

    mongo_handler.save_entry(data_three_filter_logicals_company_code)

    assert mongo_mock.collection.find().count() == 1


def test_database_insert_same(data_three_filter_logicals_company_code):
    mongo_mock = MongoDBMock()
    mongo_handler = MongoDBHandler(mongo_mock)

    mongo_handler.save_entry(data_three_filter_logicals_company_code)
    mongo_handler.save_entry(data_three_filter_logicals_company_code)

    assert mongo_mock.collection.find().count() == 1


def test_database_insert_different(data_three_filter_logicals_company_code, data_single_filter_logical_company_code):
    mongo_mock = MongoDBMock()
    mongo_handler = MongoDBHandler(mongo_mock)

    mongo_handler.save_entry(data_three_filter_logicals_company_code)
    mongo_handler.save_entry(data_single_filter_logical_company_code)

    assert mongo_mock.collection.find().count() == 2


def test_database_find_existing(data_single_filter_logical_company_code):
    mongo_mock = MongoDBMock()
    mongo_mock.collection.insert_one(data_single_filter_logical_company_code)
    mongo_handler = MongoDBHandler(mongo_mock)

    entry = mongo_handler.find_entry(ObjectId("5c61a1295f627d1db904dd39"))

    assert entry


def test_database_find_non_existing():
    mongo_mock = MongoDBMock()
    mongo_handler = MongoDBHandler(mongo_mock)

    entry = mongo_handler.find_entry(ObjectId("5c61a1295f627d1db904dd39"))

    assert not entry


def test_database_delete_existing(data_single_filter_logical_company_code):
    mongo_mock = MongoDBMock()
    mongo_mock.collection.insert_one(data_single_filter_logical_company_code)
    mongo_handler = MongoDBHandler(mongo_mock)

    deleted_num = mongo_handler.delete_entry(ObjectId("5c61a1295f627d1db904dd39"))

    assert deleted_num == 1


def test_database_delete_non_existing(data_single_filter_logical_company_code):
    mongo_mock = MongoDBMock()
    mongo_handler = MongoDBHandler(mongo_mock)

    deleted_num = mongo_handler.delete_entry(ObjectId("5c61a1295f627d1db904dd39"))

    assert deleted_num == 0


def test_database_delete_worst_entries_zero_from_two(data_single_filter_logical_company_code, data_three_filter_logicals_company_code):
    mongo_mock = MongoDBMock()
    mongo_mock.collection.insert_many([data_single_filter_logical_company_code, data_three_filter_logicals_company_code])
    mongo_handler = MongoDBHandler(mongo_mock)

    mongo_handler.delete_worst_entries(0)

    assert mongo_mock.collection.find().count() == 2


def test_database_delete_worst_entries_one_from_two(data_single_filter_logical_company_code, data_three_filter_logicals_company_code):
    mongo_mock = MongoDBMock()
    mongo_mock.collection.insert_many([data_single_filter_logical_company_code, data_three_filter_logicals_company_code])
    mongo_handler = MongoDBHandler(mongo_mock)

    mongo_handler.delete_worst_entries(1)

    assert mongo_mock.collection.find().count() == 1


def test_database_delete_worst_entries_two_from_two(data_single_filter_logical_company_code, data_three_filter_logicals_company_code):
    mongo_mock = MongoDBMock()
    mongo_mock.collection.insert_many([data_single_filter_logical_company_code, data_three_filter_logicals_company_code])
    mongo_handler = MongoDBHandler(mongo_mock)

    mongo_handler.delete_worst_entries(2)

    assert mongo_mock.collection.find().count() == 0


def test_database_delete_collection(data_single_filter_logical_company_code, data_three_filter_logicals_company_code):
    mongo_mock = MongoDBMock()
    mongo_mock.collection.insert_many([data_single_filter_logical_company_code, data_three_filter_logicals_company_code])
    mongo_handler = MongoDBHandler(mongo_mock)

    mongo_handler.delete_collection()

    assert mongo_mock.collection.find().count() == 0


def test_database_total_entries_two(data_single_filter_logical_company_code, data_three_filter_logicals_company_code):
    mongo_mock = MongoDBMock()
    mongo_mock.collection.insert_many([data_single_filter_logical_company_code, data_three_filter_logicals_company_code])
    mongo_handler = MongoDBHandler(mongo_mock)

    total_entries = mongo_handler.total_entries()

    assert total_entries == 2


def test_database_total_score_eleven(data_single_filter_logical_company_code, data_three_filter_logicals_company_code):
    mongo_mock = MongoDBMock()
    mongo_mock.collection.insert_many([data_single_filter_logical_company_code, data_three_filter_logicals_company_code])
    mongo_handler = MongoDBHandler(mongo_mock)

    total_score = mongo_handler.total_score()

    assert total_score == 11


@pytest.mark.skip(reason="Cannot mock random sampling")
# relevant to issue https://github.com/SAP/odfuzz/issues/9
def test_database_sample_filter_entries_no_exclude(data_single_filter_logical_company_code, data_two_filter_logicals_company_code,
                                                   data_three_filter_logicals_company_code, data_search_output_set):
    mongo_mock = MongoDBMock()
    mongo_mock.collection.insert_many([data_single_filter_logical_company_code, data_two_filter_logicals_company_code,
                                       data_three_filter_logicals_company_code, data_search_output_set])
    mongo_handler = MongoDBHandler(mongo_mock)

    entry = mongo_handler.sample_filter_entry('C_CorrespondenceCompanyCodeVH', 1)

    assert entry == data_three_filter_logicals_company_code


def test_database_find_best_two(data_single_filter_logical_company_code, data_single_filter_logical_company_code_error,
                                data_search_correspondence_company_code_error):
    mongo_mock = MongoDBMock()
    mongo_mock.collection.insert_many([data_single_filter_logical_company_code, data_single_filter_logical_company_code_error,
                                       data_search_correspondence_company_code_error])
    mongo_handler = MongoDBHandler(mongo_mock)

    best_two_entries = mongo_handler.find_best_entries('C_CorrespondenceCompanyCodeVH')

    assert best_two_entries == [data_single_filter_logical_company_code_error, data_search_correspondence_company_code_error]


def test_database_find_best_three(data_single_filter_logical_company_code, data_two_filter_logicals_company_code,
                                data_search_correspondence_company_code_error, data_inlinecount_correspondence_company_code_error,
                                data_single_filter_logical_company_code_error):
    mongo_mock = MongoDBMock()
    mongo_mock.collection.insert_many([data_single_filter_logical_company_code, data_two_filter_logicals_company_code,
                                       data_search_correspondence_company_code_error, data_single_filter_logical_company_code_error,
                                       data_inlinecount_correspondence_company_code_error])
    mongo_handler = MongoDBHandler(mongo_mock)

    best_three_entries = mongo_handler.find_best_entries('C_CorrespondenceCompanyCodeVH')

    assert best_three_entries == [data_single_filter_logical_company_code_error, data_search_correspondence_company_code_error,
                                  data_inlinecount_correspondence_company_code_error]


def test_distinct_errorous_two_entities(data_single_filter_logical_company_code_error, data_search_output_set_error):
    mongo_mock = MongoDBMock()
    mongo_mock.collection.insert_many([data_single_filter_logical_company_code_error, data_search_output_set_error])
    mongo_handler = MongoDBHandler(mongo_mock)

    distinct_entities = mongo_handler.find_distinct_errorous_entity_names()

    assert set(distinct_entities) == set(['C_CorrespondenceOutputSet', 'C_CorrespondenceCompanyCodeVH'])
