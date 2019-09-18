from datetime import datetime
from typing import List, Type, Dict, Any, Union

from ...core.model import T
from ...core.models.submission import Submission
from ...core.models.submission_file import SubmissionFile


class DbSubmission(Submission):

    def __init__(self,
                 submission_id: str,
                 user_id: str,
                 date: datetime,
                 status: str,
                 qc_status: str,
                 path: str,
                 store_user_path: str,
                 files: List[SubmissionFile],
                 id_: str = None,
                 publication_date: Union[datetime, str] = None,
                 allow_publication: bool = None):
        super().__init__(submission_id, user_id, date, status, qc_status, publication_date,
                         allow_publication, [])

        self._id = id_
        self._path = path
        self._store_sub_path = store_user_path
        self._files = files

    #def __repr__(self):
    #    return json.dumps(self.to_dict())

    @property
    def next_index(self):
        max_index = 0
        for f in self.files:
            if f.index > max_index:
                max_index = f.index

        return max_index + 1

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

    @property
    def store_sub_path(self):
        return self._store_sub_path

    @store_sub_path.setter
    def store_sub_path(self, value: str):
        self._store_sub_path = value

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

    @classmethod
    def from_dict(cls: Type[T], dictionary: Dict[str, Any]):
        subm = super().from_dict(dictionary)

        subm_files_array = []
        files_array = dictionary["files"]
        for file_dict in files_array:
            submf = SubmissionFile.from_dict(file_dict)
            subm_files_array.append(submf)

        path = dictionary["path"]
        id_ = None
        if "id" in dictionary:
            id_ = dictionary["id"]

        return DbSubmission(submission_id=subm.submission_id,
                            user_id=subm.user_id,
                            date=subm.date,
                            status=subm.status,
                            qc_status=subm.qc_status,
                            path=path,
                            store_user_path=dictionary['store_sub_path'],
                            publication_date=subm.publication_date,
                            allow_publication=subm.allow_publication,
                            files=subm_files_array,
                            id_=id_)

    def to_submission(self):
        file_refs = []
        for file in self._files:
            file_refs.append(file.to_ref())

        subm = Submission(submission_id=self._submission_id,
                          user_id=self._user_id,
                          date=self._date,
                          qc_status=self._qc_status,
                          status=self._status,
                          publication_date=self._publication_date,
                          allow_publication=self._allow_publication,
                          file_refs=file_refs)
        return subm
