from abc import abstractmethod
from typing import Optional, List

from ocdb.core.db.db_links import DbLinks
from ocdb.core.db.db_submission import DbSubmission
from ocdb.core.db.db_user import DbUser
from ocdb.core.models.submission_file import SubmissionFile
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
    def get_submission_file_by_filename(self, submission_id: str, file_name: str) -> Optional[SubmissionFile]:
        """Get existing submission_file by file name."""

    @abstractmethod
    def get_submissions(self, offset: int = None, count: int = None, user_id: str = None, query_column: str = None,
                        query_value: str = None, sort_column: str = None, sort_order: str = None) -> List[DbSubmission]:
        """Get existing submissions for user."""

    @abstractmethod
    def get_submissions_for_user(self, user_name: str, offset: int = None, count: int = None) -> List[DbSubmission]:
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

    @abstractmethod
    def add_user(self, user: DbUser) -> str:
        """Add new user"""

    @abstractmethod
    def get_user_names(self) -> List[str]:
        """Add new user"""

    @abstractmethod
    def update_user(self, user: DbUser) -> bool:
        """Update existing user"""

    @abstractmethod
    def delete_user(self, user_name: str) -> bool:
        """Get existing user by User Name."""

    @abstractmethod
    def get_user(self, user_name: str, password: str = None) -> DbUser:
        """Get existing user by User Name."""

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> DbUser:
        """Get existing user by User Name."""

    @abstractmethod
    def get_links(self) -> DbLinks:
        """Get Links page content"""

    @abstractmethod
    def update_links(self, content: DbLinks) -> bool:
        """Update Links page content"""
