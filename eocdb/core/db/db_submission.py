from datetime import datetime
from typing import List, Type, Dict, Any

from ...core.model import T
from ...core.models.submission import Submission
from ...core.models.submission_file import SubmissionFile


class DbSubmission(Submission):

    def __init__(self,
                 submission_id: str,
                 user_id: int,
                 date: datetime,
                 status: str,
                 qc_status: str,
                 path: str,
                 files: List[SubmissionFile],
                 id_: str = None):
        super().__init__(submission_id, user_id, date, status, qc_status, [], id_)

        self._path = path
        self._files = files

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, value: SubmissionFile):
        self._files = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value: str):
        self._path = value

    @classmethod
    def from_dict(cls: Type[T], dictionary: Dict[str, Any]):
        subm = super().from_dict(dictionary)

        subm_files_array = []
        files_array = dictionary["files"]
        for file_dict in files_array:
            submf = SubmissionFile.from_dict(file_dict)
            subm_files_array.append(submf)

        path = dictionary["path"]

        return DbSubmission(submission_id=subm.submission_id,
                            user_id=subm.user_id,
                            date=subm.date,
                            status=subm.status,
                            qc_status=subm.qc_status,
                            path=path,
                            files=subm_files_array,
                            id_=subm.id)

    def to_submission(self):
        file_refs = []
        for file in self._files:
            file_refs.append(file.to_ref())

        subm = Submission(submission_id=self._submission_id,
                          user_id=self._user_id,
                          date=self._date,
                          qc_status=self._qc_status,
                          status=self._status,
                          file_refs=file_refs)
        return subm
