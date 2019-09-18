from ..model import Model


class SubmissionFileRef(Model):

    def __init__(self, index: int,
                 submission_id: str,
                 filename: str,
                 filetype: str,
                 status: str):
        self._index = index
        self._submission_id=submission_id
        self._filename = filename
        self._filetype = filetype
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