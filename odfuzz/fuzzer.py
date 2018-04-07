import requests
import pymongo
import random
import time
import os

from odfuzz.entities import Builder, Restricitons
from odfuzz.exceptions import DispatcherError
from odfuzz.constants import ENV_USERNAME, ENV_PASSWORD, MONGODB_NAME


class Manager(object):
    def __init__(self, arguments):
        self._dispatcher = Dispatcher(arguments.service)
        self._restrictions = Restrictions(arguments.restrictions)

    def start(self):
        builder = Builder(self._restrictions, self._dispatcher)

        mongo_client = pymongo.MongoClient()
        mongo_database = mongo_client[MONGODB_NAME]

        fuzzer = Fuzzer(self._dispatcher, builder, mongo_database)
        fuzzer.run()


class Fuzzer(object):
    def __init__(self, dispatcher, builder, mongodb, **kwargs):
        self._dispatcher = dispatcher
        self._builder = builder
        self._mongodb = mongodb

        if kwargs.get('async'):
            self._generate = self._generate_multiple
        else:
            self._generate = self._generate_single

        self._tests_num = 0
        self._fails_num = 0

    def run(self):
        time_seed = time.time()
        random.seed(time_seed)

    def _generate_multiple(self):
        pass

    def _generate_single(self):
        pass


class Dispatcher(object):
    def __init__(self, service, sap_certificate=None):
        self._service = service.rstrip('/') + '/'
        self._sap_certificate = sap_certificate

        self._session = requests.Session()
        self._session.auth = (os.getenv(ENV_USERNAME), os.getenv(ENV_PASSWORD))
        self._session.verify = self._get_sap_certificate()

    @property
    def session(self):
        return self._session

    @property
    def service(self):
        return self._service

    def send(self, method, query, **kwargs):
        url = self._service + query
        try:
            response = self._session.request(method, url, **kwargs)
        except requests.exceptions.RequestException as requests_ex:
            raise DispatcherError('An exception was raised while sending HTTP {}: {}'
                                  .format(method, requests_ex))
        return response

    def get(self, query, **kwargs):
        return self.send('GET', query, **kwargs)

    def post(self, query, **kwargs):
        return self.send('POST', query, **kwargs)

    def _get_sap_certificate(self):
        if not self._sap_certificate:
            self_dir = os.path.dirname(__file__)
            candidate_path = os.path.join(self_dir, '../config/security/ca_sap_root_base64.crt')
            if not os.path.isfile(candidate_path):
                return None
            self._sap_certificate = candidate_path
        return self._sap_certificate
