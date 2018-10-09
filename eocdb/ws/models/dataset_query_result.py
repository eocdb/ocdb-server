from typing import List

from .dataset_query import DatasetQuery
from .dataset_ref import DatasetRef
from ..model import Model


class DatasetQueryResult(Model):

    def __init__(self):
        self._total_count = None
        self._datasets = None
        self._query = None

    @property
    def total_count(self) -> int:
        return self._total_count

    @total_count.setter
    def total_count(self, value: int):
        self._total_count = value

    @property
    def datasets(self) -> List[DatasetRef]:
        return self._datasets

    @datasets.setter
    def datasets(self, value: List[DatasetRef]):
        self._datasets = value

    @property
    def query(self) -> DatasetQuery:
        return self._query

    @query.setter
    def query(self, value: DatasetQuery):
        self._query = value
