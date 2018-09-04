"""This module contains a wrapper of mongoDB client."""

import sys
import logging
import random
import uuid
import pymongo
import pymongo.errors

from odfuzz.constants import MONGODB_NAME, PARTS_NUM, FILTER_SAMPLE_SIZE


class CollectionCreator(object):
    def __init__(self, service_name):
        self._service_name = service_name
        self._collection_name = None

    def create(self):
        random_uuid = str(uuid.UUID(int=random.getrandbits(128), version=4))
        self._collection_name = '{}-{}'.format(self._service_name, random_uuid)
        return self._collection_name

    def get_cached(self):
        return self._collection_name


class MongoClient(object):
    """A NoSQL database client."""

    def __init__(self, collection_name):
        self._mongodb = pymongo.MongoClient()
        self._collection = self._mongodb[MONGODB_NAME][collection_name]

    @property
    def collection(self):
        return self._collection

    def remove_collection(self):
        # TODO: use drop() instead
        self._collection.remove({})

    def save_document(self, query_dict):
        # TODO: create custom ObjectId with random generator and use upsert() instead of insert()
        try:
            if self._collection.find(query_dict).count() == 0:
                self._collection.insert_one(query_dict)
        except pymongo.errors.DocumentTooLarge:
            logging.info('The document is too large: {} bytes'.format(sys.getsizeof(query_dict)))

    def query_by_id(self, query_id):
        cursor = self._collection.find({'_id': query_id})

        cursor_list = list(cursor)
        if cursor_list:
            return cursor_list[0]
        return None

    def overall_score(self):
        cursor = self._collection.aggregate(
            [
                {'$project': {'score': 1}},
                {'$group': {'_id': None, 'overall': {'$sum': '$score'}}}
            ])
        cursor_list = list(cursor)
        if cursor_list:
            population_overall = cursor_list[0]['overall']
        else:
            population_overall = 0
        return population_overall

    def total_queries(self):
        return self._collection.find().count()

    def best_filter_sample_query(self, entity_set_name, without):
        queries = list(self._collection.aggregate(
            [
                {'$match': {'entity_set': entity_set_name, '_id': {'$ne': without},
                            '_$filter.parts': {'$exists': True},
                            '$expr': {'$gte': [{'$size': '$_$filter.parts'}, PARTS_NUM]}}},
                {'$sample': {'size': FILTER_SAMPLE_SIZE}},
                {'$sort': {'score': pymongo.DESCENDING}},
                {'$limit': 1}
            ]))
        if queries:
            return queries[0]
        else:
            return None

    def remove_weakest_queries(self, number):
        cursor = self._collection.find().sort('score', pymongo.ASCENDING).limit(number)

        ids_to_remove = []
        for query in cursor:
            ids_to_remove.append(query['_id'])
        self._collection.delete_many({'_id': {'$in': ids_to_remove}})

    def existing_entities(self):
        cursor = self._collection.aggregate(
            [
                {'$match': {'http': '500'}},
                {'$group': {'_id': '$entity_set'}}
            ])

        entities = []
        for entity in cursor:
            entities.append(entity['_id'])
        return entities

    # TODO: change name of the method
    def sorted_queries_by_entity(self, entity_set_name, queries_num):
        cursor = self._collection.find({'entity_set': entity_set_name,
                                        'http': '500'}).sort([('score', -1)]).limit(queries_num)
        return list(cursor)

    def remove_by_id(self, query_id):
        result = self._collection.delete_one({'_id': query_id})
        return result.deleted_count
