"""This module defines an interface for local databases. At the moment, the only supported database is mongoDB."""

import random
import uuid


# pylint: disable=unused-import
from abc import ABCMeta, abstractmethod
from pymongo import errors, MongoClient, ASCENDING, DESCENDING

from odfuzz.constants import MONGODB_NAME, FILTER_PARTS_NUM, FILTER_SAMPLE_SIZE, MAX_BEST_QUERIES


class CollectionCreator:
    def __init__(self, service_name):
        self._service_name = service_name
        self._collection_name = None

    def create_new(self):
        random_uuid = str(uuid.UUID(int=random.getrandbits(128), version=4))
        self._collection_name = '{}-{}'.format(self._service_name, random_uuid)
        return self._collection_name

    def get_cached(self):
        return self._collection_name


class DatabaseOperationsHandler:
    @abstractmethod
    def save_entry(self, data):
        pass
    
    @abstractmethod
    def find_entry(self, id):
        pass

    @abstractmethod
    def delete_entry(self, id):
        pass
    
    @abstractmethod
    def delete_worst_entries(self, number):
        pass

    @abstractmethod
    def delete_collection(self):
        pass

    @abstractmethod
    def total_entries(self):
        pass
    
    @abstractmethod
    def total_score(self):
        pass
    
    @abstractmethod
    def sample_filter_entry(self, entity_set_name, exclude_id):
        pass
    
    @abstractmethod
    def find_best_entries(self):
        pass


class MongoDB:
    def __init__(self, collection_name):
        mongodb = MongoClient(serverSelectionTimeoutMS=10000)
        mongodb.server_info()

        self._collection = mongodb[MONGODB_NAME][collection_name]
    
    @property
    def collection(self):
        return self._collection


class MongoDBHandler(DatabaseOperationsHandler):
    def __init__(self, mongodb_client):
        self._collection = mongodb_client.collection
    
    def save_entry(self, data):
        if self._collection.find(data).count() == 0:
            self._collection.insert_one(data)
    
    def find_entry(self, id):
        queries = list(self._collection.find({'_id': id}))
        return next(iter(queries), None)
    
    def delete_entry(self, id):
        result = self._collection.delete_one({'_id': id})
        return result.deleted_count
    
    def delete_worst_entries(self, number):
        if number > 0:
            queries = self._collection.find().sort('score', ASCENDING).limit(number)

            ids_to_remove = [query['_id'] for query in queries]
            self._collection.delete_many({'_id': {'$in': ids_to_remove}})

    def delete_collection(self):
        self._collection.drop()

    def total_entries(self):
        return self._collection.find().count()
    
    def total_score(self):
        scores = list(self._collection.aggregate([
            {'$project': {'score': 1}},
            {'$group': {'_id': None, 'overall': {'$sum': '$score'}}}
        ]))
        if  scores:
            overall_score = scores[0]['overall']
        else:
            overall_score = 0
        return overall_score
    
    def sample_filter_entry(self, entity_set_name, exclude_id):
        queries = list(self._collection.aggregate([
            {'$match': {'entity_set': entity_set_name, '_id': {'$ne': exclude_id},
                        '_$filter.parts': {'$exists': True},
                        '$expr': {'$gte': [{'$size': '$_$filter.parts'}, FILTER_PARTS_NUM]}}},
            {'$sample': {'size': FILTER_SAMPLE_SIZE}},
            {'$sort': {'score': DESCENDING}}, {'$limit': 1}
        ]))
        return next(iter(queries), None)
    
    def find_best_entries(self, entity_set_name):
        queries = self._collection.find(
            {'entity_set': entity_set_name, 'http': '500'}).sort([('score', DESCENDING)]).limit(MAX_BEST_QUERIES)
        return list(queries)

    def find_distinct_errorous_entity_names(self):
        entity_names = self._collection.aggregate([
            {'$match': {'http': '500'}},
            {'$group': {'_id': '$entity_set'}}
        ])
        return [entity_name['_id'] for entity_name in entity_names]
