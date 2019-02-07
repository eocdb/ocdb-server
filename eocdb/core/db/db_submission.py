from datetime import datetime
from typing import List

from ...core.models.submission_file import SubmissionFile
from ...core.models.submission import Submission


class DbSubmission(Submission):

    def __init__(self,
                 submission_id: str,
                 user_id: int,
                 date: datetime,
                 status: str,
                 files: List[SubmissionFile]):
        super().__init__(submission_id, user_id, date, status, [])

        self._files = files

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, value: SubmissionFile):
        self._files = value

    def to_submission(self):
        file_refs = []
        for file in self._files:
            file_refs.append(file.to_ref())

        subm = Submission(submission_id=self._submission_id,
                          user_id=self._user_id,
                          date=self._date,
                          status=self._status,
                          file_refs=file_refs)
        return subm
