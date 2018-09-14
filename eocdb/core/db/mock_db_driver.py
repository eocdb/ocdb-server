from datetime import datetime
from typing import List

from eocdb.core import Dataset
from eocdb.core.db.errors import DatabaseError
from eocdb.core.db.db_dataset import DbDataset
from eocdb.core.db.db_driver import DbDriver


class MockDbDriver(DbDriver):

    def init(self, **config):
        pass

    def update(self, **config):
        pass

    def dispose(self):
        pass

    def get(self, query_expression=None) -> List[Dataset]:
        if "trigger_error" == query_expression:
            raise DatabaseError("Triggering a test error")

        if not "ernie" in query_expression:
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

    def insert(self, document):
        pass