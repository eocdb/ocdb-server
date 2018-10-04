from typing import List
from urllib.parse import urlparse

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from eocdb.core import Dataset
from eocdb.core.db.errors import OperationalError
from eocdb.core.db.db_dataset import DbDataset
from eocdb.core.db.db_driver import DbDriver


class MongoDbDriver(DbDriver):

    def __init__(self):
        self.client = None
        self.collection = None
        self.host_name = None
        self.port = None

    def init(self, **config):
        self._extract_param_values(config)
        self.connect()

    def update(self, **config):
        self._extract_param_values(config)
        self.close()
        self.connect()

    def dispose(self):
        self.close()

    def connect(self):
        if self.client is not None:
            raise OperationalError("Database already connected, do not call this twice!")

        self.client = MongoClient(self.host_name, self.port)

        try:
            # @trello: Resolve call hanging when requesting MongoDb server up
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
        except ConnectionFailure:
            raise Exception("Database server not accessible")

        self.db = self.client.eocdb
        self.collection = self.db.sb_datasets

    def close(self):
        if self.client is not None:
            self.client.close()

    def clear(self):
        if self.client is not None:
            self.collection.drop()

    def insert(self, document):
        self.collection.insert_one(document)

    def get(self, query_expression=None) -> List[Dataset]:
        if query_expression is None:
            cursor = self.collection.find()
        else:
            term_1 = query_expression.term1
            name_1 = term_1.name
            min_1 = term_1.start_value
            max_1 = term_1.end_value

            term_2 = query_expression.term2
            name_2 = term_2.name
            min_2 = term_2.start_value
            max_2 = term_2.end_value

            cursor = self.collection.find({'records.' + name_1: {"$gt" : min_1, "$lt" : max_1}, "records." + name_2: {"$gt" : min_2, "$lt" : max_2}})

        results = []
        for record in cursor:
            dataset = DbDataset()
            dataset.set_metadata(record)
            results.append(dataset)

        return results

    def _extract_param_values(self, config):
        url = config.get('url')
        url_result = urlparse(url)
        self.host_name = url_result.hostname
        self.port = url_result.port