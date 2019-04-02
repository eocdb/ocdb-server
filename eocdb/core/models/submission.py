from datetime import datetime
from typing import List, Optional

from ...core.model import Model
from ...core.models.submission_file_ref import SubmissionFileRef

TYPE_MEASUREMENT = 'MEASUREMENT'
TYPE_DOCUMENT = 'DOCUMENT'


class Submission(Model):

    def __init__(self,
                 submission_id: str,
                 user_id: int,
                 date: datetime,
                 status: str,
                 qc_status: str,
                 publication_date: datetime,
                 allow_publication: bool,
                 file_refs: List[SubmissionFileRef]):
        self._submission_id = submission_id
        self._user_id = user_id
        self._date = date
        self._status = status
        self._publication_date = publication_date
        self._qc_status = qc_status
        self._file_refs = file_refs
        self._allow_publication = allow_publication

    @property
    def submission_id(self):
        return self._submission_id

    @submission_id.setter
    def submission_id(self, value: str):
        self._submission_id = value

    @property
    def allow_publication(self) -> Optional[bool]:
        return self._allow_publication

    @allow_publication.setter
    def allow_publication(self, value: bool):
        self._allow_publication = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value: int):
        self._user_id = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value: datetime):
        self._date = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: str):
        self._status = value

    @property
    def publication_date(self) -> Optional[datetime]:
        return self._publication_date

    @publication_date.setter
    def publication_date(self, value: datetime):
        self._publication_date = value

    @property
    def qc_status(self):
        return self._qc_status

    @qc_status.setter
    def qc_status(self, value: str):
        self._qc_status = value

    @property
    def file_refs(self):
        return self._file_refs

    @file_refs.setter
    def file_refs(self, value: List[SubmissionFileRef]):
        self._file_refs = value
