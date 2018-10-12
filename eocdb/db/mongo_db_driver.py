from typing import List, Any, Dict

import pymongo
import pymongo.errors

from eocdb.core import Dataset
from eocdb.core.db.db_dataset import DbDataset
from eocdb.core.db.db_driver import DbDriver
from eocdb.core.db.errors import OperationalError


class MongoDbDriver(DbDriver):

    def __init__(self):
        self._db = None
        self._client = None
        self._collection = None
        self._config = None

    def init(self, **config):
        self._set_config(config)
        self.connect()

    def update(self, **config):
        self._set_config(config)
        self.close()
        self.connect()

    def dispose(self):
        self.close()

    def connect(self):
        if self._client is not None:
            raise OperationalError("Database already connected")

        if self._config.get("mock", False):
            import mongomock
            self._client = mongomock.MongoClient()
        else:
            self._client = pymongo.MongoClient(**self._config)
            try:
                # @trello: Resolve call hanging when requesting MongoDb server up
                # The ismaster command is cheap and does not require auth.
                self._client.admin.command('ismaster')
            except pymongo.errors.ConnectionFailure as e:
                raise RuntimeError("Database connection failure") from e

        # Create database "eocdb"
        self._db = self._client.eocdb
        # Create collection "eocdb.sb_datasets"
        self._collection = self._client.eocdb.sb_datasets

    def close(self):
        if self._client is not None:
            self._client.close()

    def clear(self):
        if self._client is not None:
            self._collection.drop()

    def insert(self, document):
        self._collection.insert_one(document)

    def get(self, query_expression=None) -> List[Dataset]:
        if query_expression is None:
            cursor = self._collection.find()
        else:
            term_1 = query_expression.term1
            name_1 = term_1.name
            min_1 = term_1.start_value
            max_1 = term_1.end_value

            term_2 = query_expression.term2
            name_2 = term_2.name
            min_2 = term_2.start_value
            max_2 = term_2.end_value

            cursor = self._collection.find(
                {'records.' + name_1: {"$gt": min_1, "$lt": max_1}, "records." + name_2: {"$gt": min_2, "$lt": max_2}})

        results = []
        for record in cursor:
            dataset = DbDataset()
            dataset.set_metadata(record)
            results.append(dataset)

        return results

    def _set_config(self, config: Dict[str, Any]):
        for key in ("url", "uri"):
            uri = config.get(key)
            if uri:
                #
                # From MongoDB.__init__() doc:
                #
                #  `host` (optional): hostname or IP address or Unix domain socket
                #     path of a single mongod or mongos instance to connect to, or a
                #     mongodb URI, or a list of hostnames / mongodb URIs. If `host` is
                #     an IPv6 literal it must be enclosed in '[' and ']' characters
                #     following the RFC2732 URL syntax (e.g. '[::1]' for localhost).
                #
                config["host"] = uri
                del config[key]
        self._config = config
