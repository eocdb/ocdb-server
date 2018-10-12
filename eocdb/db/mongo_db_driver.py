import uuid
from typing import List, Any, Dict, Optional

import pymongo
import pymongo.errors

from ..core import Dataset as _Dataset
from ..core.db.db_dataset import DbDataset
from ..core.db.db_driver import DbDriver
from ..core.db.errors import OperationalError
from ..core.deprecated import deprecated
from ..core.models.bucket import Bucket
from ..core.models.dataset import Dataset
from ..core.models.dataset_query import DatasetQuery
from ..core.models.dataset_query_result import DatasetQueryResult
from ..core.models.dataset_ref import DatasetRef
from ..core.models.dataset_validation_result import DatasetValidationResult


class MongoDbDriver(DbDriver):

    def add_dataset(self, dataset: Dataset) -> DatasetValidationResult:
        """Add dataset."""
        # TODO by forman: validate dataset here or do it outside? If latter,
        #                 return type "DatasetValidationResult" should be replaced by "List[DatasetRef]"
        validation_result = DatasetValidationResult()
        validation_result.status = "OK"
        validation_result.issues = []
        # TODO by forman: is there a MongoDB specific way to gen IDs?
        dataset.id = str(uuid.uuid4())
        self._collection.insert_one(dataset.to_dict())
        return validation_result

    def get_dataset(self, dataset_id) -> Optional[Dataset]:
        # TODO by forman: use find() with query filter here to find docs by "id"
        cursor = self._collection.find()
        for dataset_dict in cursor:
            if dataset_dict.get("id") == dataset_id:
                return Dataset.from_dict(dataset_dict)
        return None

    def remove_dataset(self, dataset_id):
        # TODO by forman: remove dataset here
        return

    def find_datasets(self, query: DatasetQuery) -> DatasetQueryResult:
        """Find datasets for given query and return list of dataset references."""

        if query.offset is None:
            start_index = 1
        else:
            start_index = query.offset - 1

        if query.count is None:
            end_index = -1
        else:
            # Note, for count=0 we will get an empty result set, which is desired.
            end_index = start_index + query.count - 1

        query_filter = None
        # TODO by forman: setup query_filter from query

        cursor = self._collection.find(query_filter)

        dataset_refs = []
        index = 0
        for dataset_dict in cursor:
            # TODO by forman: is there a MongoDB specifc way to get results for start_index <= index <= end_index?
            if index >= start_index and (end_index == -1 or index <= end_index):
                id_ = dataset_dict.get("id")
                bucket_dict = dataset_dict.get("bucket")
                name = dataset_dict.get("name")
                dataset_ref = DatasetRef()
                dataset_ref.id = id_
                dataset_ref.bucket = Bucket.from_dict(bucket_dict) if bucket_dict else None
                dataset_ref.name = name
                dataset_refs.append(dataset_ref)
            index += 1

        result = DatasetQueryResult()
        result.query = query
        result.total_count = index
        result.datasets = dataset_refs
        return result

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

    @deprecated
    def insert(self, document):
        self._collection.insert_one(document)

    @deprecated
    def get(self, query_expression=None) -> List[_Dataset]:
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
