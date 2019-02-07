from abc import abstractmethod
from typing import Optional

from ..models.submission import Submission
from .. import Service
from ..models import DatasetQueryResult
from ..models.dataset import Dataset
from ..models.dataset_query import DatasetQuery


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
    def find_datasets(self, query: DatasetQuery) -> DatasetQueryResult:
        """Find datasets for given query and return list of dataset references."""

    @abstractmethod
    def add_submission(self, submission: Submission) -> str:
        """Add new submission file and return ID."""

    @abstractmethod
    def get_submission(self, submission_id: str) -> Optional[Submission]:
        """Get existing submission_file by ID."""
