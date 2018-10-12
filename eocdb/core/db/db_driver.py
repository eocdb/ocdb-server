from abc import abstractmethod
from typing import List, Optional

from .. import Dataset as _Dataset
from .. import Service, Dataset
from ..deprecated import deprecated
from ..models.dataset_query import DatasetQuery
from ..models.dataset_ref import DatasetRef


class DbDriver(Service):

    @abstractmethod
    def add_dataset(self, dataset: Dataset):
        """Add dataset."""

    @abstractmethod
    def update_dataset(self, dataset: Dataset) -> bool:
        """Update dataset."""

    @abstractmethod
    def delete_dataset(self, dataset_id) -> bool:
        """Delete dataset by ID."""

    @abstractmethod
    def get_dataset(self, dataset_id) -> Optional[Dataset]:
        """Get dataset by ID."""

    @abstractmethod
    def find_datasets(self, query: DatasetQuery) -> List[DatasetRef]:
        """Find datasets for given query and return list of dataset references."""

    @abstractmethod
    @deprecated
    def get(self, query_expression=None) -> List[_Dataset]:
        """Query database for list of datasets matching the query_expression"""

    @abstractmethod
    @deprecated
    def insert(self, document):
        """Insert one document into database"""
