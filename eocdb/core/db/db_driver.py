from abc import abstractmethod
from typing import Optional, List

from eocdb.core.db.db_submission import DbSubmission
from eocdb.core.models.submission_file import SubmissionFile
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
    def add_submission(self, submission: DbSubmission) -> str:
        """Add new submission file and return ID."""

    @abstractmethod
    def get_submission_file(self, submission_id: str, index: int) -> Optional[SubmissionFile]:
        """Get existing submission_file by ID."""

    @abstractmethod
    def get_submissions(self) -> List[DbSubmission]:
        """Get existing submissions for user."""

    @abstractmethod
    def get_submissions_for_user(self, user_id: int) -> List[DbSubmission]:
        """Get existing submissions for user."""

    @abstractmethod
    def get_submission(self, submission_id: str) -> Optional[DbSubmission]:
        """Get existing submission_file by ID."""

    @abstractmethod
    def delete_submission(self, submission_id: str) -> bool:
        """Delete existing submission by ID and return success."""

    @abstractmethod
    def update_submission(self, submission: DbSubmission) -> bool:
        """Get existing submission_file by ID."""
