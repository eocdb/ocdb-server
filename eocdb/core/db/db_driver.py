from abc import abstractmethod
from typing import List, Optional

from .. import Dataset as _Dataset
from .. import Service, Dataset
from ..deprecated import deprecated
from ..models.dataset_query import DatasetQuery
from ..models.dataset_ref import DatasetRef
from ..models.dataset_validation_result import DatasetValidationResult


class DbDriver(Service):

    @abstractmethod
    def get_dataset(self, dataset_id) -> Optional[Dataset]:
        """Get dataset by ID."""

    @abstractmethod
    def add_dataset(self, dataset: Dataset) -> DatasetValidationResult:
        """Add dataset."""
        # TODO by forman: Decide if the dataset validation go into the DbDriver interface or
        #                 shall it have its own, DB-independent package "val"?

    @abstractmethod
    def remove_dataset(self, dataset_id):
        """Remove dataset by ID."""

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
