from eocdb.core.models.submission_file_ref import SubmissionFileRef
from ...core.model import Model
from ...core.models import DatasetValidationResult


class SubmissionFile(Model):

    def __init__(self, index: int,
                 submission_id: str,
                 filename: str,
                 status: str,
                 result: DatasetValidationResult):
        self._index = index
        self._submission_id = submission_id
        self._filename = filename
        self._status = status
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
    def status(self):
        return self._status

    @status.setter
    def status(self, value: str):
        self._status = value

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
                                 status=self._status)