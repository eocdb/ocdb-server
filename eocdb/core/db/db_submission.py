from datetime import datetime
from typing import List, Type, Dict, Any

from eocdb.core.model import T
from ...core.models.submission import Submission
from ...core.models.submission_file import SubmissionFile


class DbSubmission(Submission):

    def __init__(self,
                 submission_id: str,
                 user_id: int,
                 date: datetime,
                 status: str,
                 files: List[SubmissionFile],
                 id: str = None):
        super().__init__(submission_id, user_id, date, status, [], id)

        self._files = files

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, value: SubmissionFile):
        self._files = value

    @classmethod
    def from_dict(cls: Type[T], dictionary: Dict[str, Any]):
        subm = super().from_dict(dictionary)

        subm_files_array = []
        files_array = dictionary["files"]
        for file_dict in files_array:
            submf = SubmissionFile.from_dict(file_dict)
            subm_files_array.append(submf)

        return DbSubmission(submission_id=subm.submission_id,
                            user_id=subm.user_id,
                            date=subm.date,
                            status=subm.status,
                            files=subm_files_array,
                            id=subm.id)

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
