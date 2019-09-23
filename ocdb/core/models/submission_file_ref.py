from datetime import datetime
from typing import Optional

from ..model import Model


class SubmissionFileRef(Model):

    def __init__(self, index: int,
                 submission_id: str,
                 filename: str,
                 filetype: str,
                 status: str,
                 creationdate: Optional[datetime] = None):
        self._index = index
        self._submission_id = submission_id
        self._filename = filename
        self._filetype = filetype
        self._creationdate = creationdate
        self._status = status

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value: int):
        self._index = value

    @property
    def submission_id(self):
        return self._submission_id

    @submission_id.setter
    def submission_id(self, value: str):
        self._submission_id = value

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value: str):
        self._filename = value

    @property
    def filetype(self):
        return self._filetype

    @filetype.setter
    def filetype(self, value: str):
        self._filetype = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: str):
        self._status = value

    @property
    def creationdate(self):
        return self._creationdate

    @creationdate.setter
    def creationdate(self, value: str):
        self._creationdate = value
