from typing import Optional

from ..model import Model


class SubmissionFile(Model):

    def __init__(self,
                 submission_id: str,
                 id: str = None):
        self._submission_id = submission_id
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
    def submission_id(self, value: Optional[str]):
        self._submission_id = value
