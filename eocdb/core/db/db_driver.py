from abc import abstractmethod
from typing import List, Optional

from ..models.dataset import Dataset
from .. import Service
from ..deprecated import deprecated
from ..models.dataset_query import DatasetQuery
from ..models.dataset_ref import DatasetRef


class DbDriver(Service):

    @abstractmethod
    def add_dataset(self, dataset: Dataset) -> str:
        """Add new dataset and return ID."""

    @abstractmethod
    def update_dataset(self, dataset: Dataset) -> bool:
        """Update existing dataset and return success."""

    @abstractmethod
    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete existing dataset by ID and return success."""

    @abstractmethod
    def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        """Get existing dataset by ID."""

    @abstractmethod
    def find_datasets(self, query: DatasetQuery) -> List[DatasetRef]:
        """Find datasets for given query and return list of dataset references."""