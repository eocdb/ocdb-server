from datetime import datetime
from typing import Any, Dict, Optional, List

import bson.objectid
import numpy as np
import pymongo
import pymongo.errors

from ..core import QueryParser
from ..core.db.db_driver import DbDriver
from ..core.db.db_submission import DbSubmission
from ..core.db.errors import OperationalError
from ..core.models.dataset import Dataset
from ..core.models.dataset_query import DatasetQuery
from ..core.models.dataset_query_result import DatasetQueryResult
from ..core.models.dataset_ref import DatasetRef
from ..core.models.submission_file import SubmissionFile
from ..core.time_helper import TimeHelper
from ..db.mongo_query_generator import MongoQueryGenerator

LAT_INDEX_NAME = "_latitudes_"
LON_INDEX_NAME = "_longitudes_"
ATTRIBUTES_INDEX_NAME = "_attributes_"
TIMES_INDEX_NAME = "_times_"
USER_ID_INDEX_NAME = "_userid_"


class MongoDbDriver(DbDriver):

    def add_dataset(self, dataset: Dataset) -> str:
        dateset_dict = dataset.to_dict()
        converted_dict = MongoDbDriver._convert_times(dateset_dict)
        result = self._collection.insert_one(converted_dict)
        return str(result.inserted_id)

    def update_dataset(self, dataset: Dataset) -> bool:
        obj_id = self._obj_id(dataset.id)
        if obj_id is None:
            return False

        dataset_dict = dataset.to_dict()
        if "id" in dataset_dict:
            del dataset_dict["id"]

        result = self._collection.replace_one({"_id": obj_id}, dataset_dict, upsert=True)
        return result.modified_count == 1

    def delete_dataset(self, dataset_id: str) -> bool:
        obj_id = self._obj_id(dataset_id)
        if obj_id is None:
            return False

        result = self._collection.delete_one({'_id': obj_id})
        return result.deleted_count == 1

    def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        obj_id = self._obj_id(dataset_id)
        if obj_id is None:
            return None

        dataset_dict = self._collection.find_one({"_id": obj_id})
        if dataset_dict is not None:
            del dataset_dict["_id"]
            dataset_dict["id"] = dataset_id
            return Dataset.from_dict(dataset_dict)
        return None

    def find_datasets(self, query: DatasetQuery) -> DatasetQueryResult:
        start_index, count = MongoDbDriver._get_start_index_and_count(query)

        query_dict = self._query_converter.to_dict(query)

        cursor = self._collection.find(query_dict, skip=start_index, limit=count)
        total_num_results = self._collection.count_documents(query_dict)
        num_results = total_num_results - start_index

        if query.count == 0:
            return DatasetQueryResult({}, num_results, [], query)
        else:
            dataset_refs = []
            locations = {}
            for dataset_dict in cursor:
                ds_ref, points = self._to_dataset_ref(dataset_dict, query.geojson)
                dataset_refs.append(ds_ref)
                if points is not None:
                    feature_collection = self._to_geojson(points)
                    locations.update({ds_ref.id: feature_collection})

            return DatasetQueryResult(locations, num_results, dataset_refs, query)

    def add_submission(self, submission: DbSubmission):
        sf_dict = submission.to_dict()
        result = self._submit_collection.insert_one(sf_dict)
        return str(result.inserted_id)

    def get_submission_file(self, submission_id: str, index: int) -> Optional[SubmissionFile]:
        subm_dict = self._submit_collection.find_one({"submission_id": submission_id})
        if subm_dict is None:
            return None

        del subm_dict["_id"]
        db_submission = DbSubmission.from_dict(subm_dict)

        num_files = len(db_submission.files)
        if index < 0 or index >= num_files:
            return None

        return db_submission.files[index]

    def get_submissions(self, user_id: int) -> List[DbSubmission]:
        submissions = []
        cursor = self._submit_collection.find({"user_id": user_id})
        for subm_dict in cursor:
            del subm_dict["_id"]
            subm = DbSubmission.from_dict(subm_dict)
            submissions.append(subm)

        return submissions

    def get_submission(self, submission_id: str) -> Optional[DbSubmission]:
        subm_dict = self._submit_collection.find_one({"submission_id": submission_id})
        if subm_dict is not None:
            sf_id = subm_dict["_id"]
            del subm_dict["_id"]
            subm_dict["id"] = str(sf_id)
            return DbSubmission.from_dict(subm_dict)
        return None

    def update_submission(self, submission: DbSubmission) -> bool:
        obj_id = self._obj_id(submission.id)
        if obj_id is None:
            return False

        submission_dict = submission.to_dict()
        if "id" in submission_dict:
            submission_dict["id"] = None

        result = self._submit_collection.replace_one({"_id": obj_id}, submission_dict)
        return result.modified_count == 1

    def delete_submission(self, submission_id: str) -> bool:
        subm_dict = self._submit_collection.find_one({"submission_id": submission_id})
        if subm_dict is None:
            return False

        result = self._submit_collection.delete_one(subm_dict)
        return result.deleted_count == 1

    @staticmethod
    def _get_start_index_and_count(query) -> (int, int):
        if query.offset is None:
            start_index = 0
        elif query.offset == 0:
            raise ValueError("Page offset is out of range")
        else:
            start_index = query.offset - 1

        if query.count is None or query.count == -1:
            count = 0
        else:
            count = query.count
        return start_index, count

    @classmethod
    def _obj_id(cls, id_: str) -> Optional[bson.objectid.ObjectId]:
        try:
            return bson.objectid.ObjectId(id_)
        except bson.errors.InvalidId:
            # For sure, the given ID has not been generated by MongoDB
            return None

    def __init__(self):
        self._db = None
        self._client = None
        self._collection = None
        self._submit_collection = None
        self._config = None
        self._query_converter = MongoDbDriver.QueryConverter()

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
        self._submit_collection = self._client.eocdb.submission_files
        self._ensure_indices()

    def close(self):
        if self._client is not None:
            self._client.close()

    def clear(self):
        if self._client is not None:
            self._collection.drop()
            self._submit_collection.drop()

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

    @staticmethod
    def _to_dataset_ref(dataset_dict, geojson=False):
        dataset_id = str(dataset_dict.get("_id"))
        path = dataset_dict.get("path")
        ds_ref = DatasetRef(dataset_id, path)

        if geojson:
            lons = dataset_dict.get("longitudes")
            lats = dataset_dict.get("latitudes")
            points = []
            for lon, lat in zip(lons, lats):
                points.append((lon, lat))
        else:
            points = None
        return ds_ref, points

    @staticmethod
    def _convert_times(dataset_dict) -> dict:
        times_array = dataset_dict["times"]
        converted_times = []
        for time in times_array:
            converted_times.append(TimeHelper.parse_datetime(time))
        dataset_dict["times"] = converted_times
        return dataset_dict

    def _ensure_indices(self):
        # the main collection
        index_information = self._collection.index_information()
        if not LON_INDEX_NAME in index_information:
            self._collection.create_index("longitude", name=LON_INDEX_NAME, background=True)
        if not LAT_INDEX_NAME in index_information:
            self._collection.create_index("latitude", name=LAT_INDEX_NAME, background=True)
        if not ATTRIBUTES_INDEX_NAME in index_information:
            self._collection.create_index("attributes", name=ATTRIBUTES_INDEX_NAME, background=True)
        if not TIMES_INDEX_NAME in index_information:
            self._collection.create_index("times", name=TIMES_INDEX_NAME, background=True)

        # the quarantane collection
        index_information = self._submit_collection.index_information()
        if not USER_ID_INDEX_NAME in index_information:
            self._submit_collection.create_index("user_id", name=USER_ID_INDEX_NAME, background=True)

    @staticmethod
    def _parse_datetime(time_string) -> datetime:
        np_datetime = np.datetime64(time_string)
        ts = (np_datetime - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        return datetime.utcfromtimestamp(ts)

    @staticmethod
    def _to_geojson(locations):
        if len(locations) == 0:
            return None

        geojson = "{'type':'FeatureCollection','features':["
        for location in locations:
            feature = "{'type':'Feature','geometry':{'type':'Point','coordinates':["
            feature += str(location[0])
            feature += ","
            feature += str(location[1])
            feature += "]}},"
            geojson += feature

        geojson = geojson[:-1]
        geojson += "]}"
        return geojson

    class QueryConverter():

        def to_dict(self, query: DatasetQuery) -> dict:
            query_dict = {}
            if query.expr is not None:
                query_generator = MongoQueryGenerator()
                q = QueryParser.parse(query.expr)
                q.accept(query_generator)
                query_dict = query_generator.query

            if query.region is not None:
                query_dict["longitudes"] = {'$gte': query.region[0], '$lte': query.region[2]}
                query_dict["latitudes"] = {'$gte': query.region[1], '$lte': query.region[3]}

            if query.time is not None:
                start_date = None
                end_date = None
                if query.time[0] is not None:
                    start_date = TimeHelper.parse_datetime(query.time[0])

                if query.time[1] is not None:
                    end_date = TimeHelper.parse_datetime(query.time[1])

                if start_date is None and end_date is None:
                    raise ValueError("Both time values are none.")

                times_dict = {}
                if start_date is not None:
                    times_dict.update({'$gte': start_date})
                if end_date is not None:
                    times_dict.update({'$lte': end_date})

                query_dict["times"] = times_dict

            if query.pgroup is not None:
                query_dict.update({'groups': {'$in': query.pgroup}})

            if query.pname is not None:
                query_dict.update({'attributes': {'$in': query.pname}})

            if query.shallow is not None:
                if query.shallow == 'no':
                    query_dict.update({'metadata.optical_depth_warning': {'$not': {'$eq': 'true'}}})
                elif query.shallow == 'exclusively':
                    query_dict.update({'metadata.optical_depth_warning': 'true'})

            if query.mtype != 'all':
                query_dict.update({'metadata.data_type': query.mtype})

            return query_dict
