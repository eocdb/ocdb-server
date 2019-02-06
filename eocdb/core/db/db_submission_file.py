from datetime import datetime
from typing import Optional

from ..model import Model


class DbSubmissionFile(Model):

    def __init__(self,
                 submission_id: str,
                 date: datetime,
                 user_id: str,
                 id: str = None):
        self._submission_id = submission_id
        self._date = date
        self._user_id = user_id
        self._id = id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value: Optional[str]):
        self._id = value

    @property
    def submission_id(self):
        return self._submission_id

    @submission_id.setter
    def submission_id(self, value: str):
        self._submission_id = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value: datetime):
        self._date = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value: str):
        self._user_id = value