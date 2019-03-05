from datetime import datetime
from typing import List, Optional

from ...core.model import Model
from ...core.models.submission_file_ref import SubmissionFileRef


class Submission(Model):

    def __init__(self,
                 submission_id: str,
                 user_id: int,
                 date: datetime,
                 status: str,
                 qc_status: str,
                 file_refs: List[SubmissionFileRef],
                 id_: str = None):
        self._id = id_
        self._submission_id = submission_id
        self._user_id = user_id
        self._date = date
        self._status = status
        self._qc_status = qc_status
        self._file_refs = file_refs

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

    @property
    def submission_id(self):
        return self._submission_id

    @submission_id.setter
    def submission_id(self, value: str):
        self._submission_id = value

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
