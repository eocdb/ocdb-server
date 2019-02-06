from datetime import datetime
from typing import List

from ...core.models.submission_file_ref import SubmissionFileRef
from ...core.model import Model


class Submission(Model):

    def __init__(self, id: str,
                 submission_id: str,
                 user_id: int,
                 date: datetime,
                 status: str,
                 files: List[SubmissionFileRef]):
        self._id = id
        self._submission_id = submission_id
        self._user_id = user_id
        self._date = date
        self._status = status
        self._files = files

    @property
    def id(self):
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
    def files(self):
        return self._files

    @files.setter
    def files(self, value: List[SubmissionFileRef]):
        self._files = value