"""This module contains a wrapper of mongoDB client."""

import sys
import logging
import pymongo
import pymongo.errors

from odfuzz.constants import MONGODB_NAME, MONGODB_COLLECTION, PARTS_NUM


class MongoClient(object):
    """A NoSQL database client."""

    def __init__(self):
        self._mongodb = pymongo.MongoClient()
        self._collection = self._mongodb[MONGODB_NAME][MONGODB_COLLECTION]

    @property
    def collection(self):
        return self._collection

    def remove_collection(self):
        self._collection.remove({})

    def save_document(self, query_dict):
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

    def queries_sample_filter(self, entity_set_name, sample_size, without):
        cursor = self._collection.aggregate(
            [
                {'$match': {'entity_set': entity_set_name, '_id': {'$ne': without},
                            '_$filter.parts': {'$exists': True},
                            '$expr': {'$gte': [{'$size': '$_$filter.parts'}, PARTS_NUM]}}},
                {'$sample': {'size': sample_size}}
            ])
        return list(cursor)

    def remove_weak_queries(self, score_average, number):
        cursor = self._collection.aggregate(
            [
                {'$project': {'score': 1}},
                {'$match': {'score': {'$lt': score_average}}},
                {'$limit': number}
            ])
        for query in cursor:
            self._collection.remove({'_id': query['_id']})

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

    def sorted_queries_by_entity(self, entity_set_name, queries_num):
        cursor = self._collection.find({'entity_set': entity_set_name,
                                        'http': '500'}).sort([('score', -1)]).limit(queries_num)
        return list(cursor)
