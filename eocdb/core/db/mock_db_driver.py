from datetime import datetime
from typing import List, Optional

from .. import Dataset as _Dataset
from ..db.db_dataset import DbDataset
from ..db.db_driver import DbDriver
from ..db.errors import DatabaseError
from ..deprecated import deprecated
from ..models.dataset import Dataset
from ..models.dataset_query import DatasetQuery
from ..models.dataset_ref import DatasetRef
from ..models.dataset_validation_result import DatasetValidationResult

# TODO by forman: decide to get rid of this class, its maintenance will be very expensive, better use mongomock

class MockDbDriver(DbDriver):

    def get_dataset(self, dataset_id) -> Optional[Dataset]:
        """Get dataset by ID."""
        raise NotImplementedError()

    def add_dataset(self, dataset: Dataset) -> DatasetValidationResult:
        """Add dataset."""
        raise NotImplementedError()

    def remove_dataset(self, dataset_id):
        """Remove dataset by ID."""
        raise NotImplementedError()

    def find_datasets(self, query: DatasetQuery) -> List[DatasetRef]:
        """Find datasets for given query and return list of dataset references."""
        raise NotImplementedError()

    @deprecated
    def get(self, query_expression=None) -> List[_Dataset]:
        if "trigger_error" == query_expression:
            raise DatabaseError("Triggering a test error")

        if "ernie" not in query_expression:
            return []

        dataset = DbDataset()
        dataset.add_metadatum("name", "ernie")
        dataset.add_metadatum("contact", "ernie@sesame_street.com")
        dataset.add_metadatum("experiment", "Counting pigments")
        dataset.add_attributes(['lon', 'lat', 'chl', 'depth'])
        dataset.add_time(datetime(2017, 5, 22, 8, 32, 44))
        dataset.add_time(datetime(2017, 5, 22, 8, 32, 48))
        dataset.add_time(datetime(2017, 5, 22, 8, 32, 52))
        dataset.add_time(datetime(2017, 5, 22, 8, 32, 56))
        dataset.add_time(datetime(2017, 5, 22, 8, 33, 0))
        dataset.add_geo_location(-34.7, 16.45)
        dataset.add_record([-34.7, 16.45, 0.345, 12.2])
        dataset.add_record([-34.7, 16.45, 0.298, 14.6])
        dataset.add_record([-34.7, 16.45, 0.307, 18.3])
        dataset.add_record([-34.7, 16.45, 0.164, 22.6])
        dataset.add_record([-34.7, 16.45, 0.108, 29.8])

        return [dataset]

    @deprecated
    def insert(self, document):
        raise NotImplementedError()

    def init(self, **config):
        pass

    def update(self, **config):
        pass

    def dispose(self):
        pass
