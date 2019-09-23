from datetime import datetime
from typing import Optional

from ...core.models.submission_file_ref import SubmissionFileRef
from ...core.model import Model
from ...core.models import DatasetValidationResult


class SubmissionFile(Model):

    def __init__(self, index: int,
                 submission_id: str,
                 filename: str,
                 filetype: str,
                 status: str,
                 result: Optional[DatasetValidationResult],
                 creationdate: Optional[datetime] = datetime.now()):
        self._index = index
        self._submission_id = submission_id
        self._filename = filename
        self._filetype = filetype
        self._status = status
        self._creationdate = creationdate
        self._result = result

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

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value: DatasetValidationResult):
        self._result = value

    def to_ref(self) -> SubmissionFileRef:
        return SubmissionFileRef(index=self._index,
                                 submission_id=self._submission_id,
                                 filename=self._filename,
                                 filetype=self._filetype,
                                 status=self._status)
