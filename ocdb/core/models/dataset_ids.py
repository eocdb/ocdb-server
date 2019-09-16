from typing import List

from ..model import Model


class DatasetIds(Model):

    def __init__(self, ids: List[str], docs: bool):
        self._id_list = ids
        self._docs = docs

    @property
    def id_list(self) -> List[str]:
        return self._id_list

    @id_list.setter
    def id_list(self, value: List[str]):
        self._id_list = value

    @property
    def docs(self) -> bool:
        return self._docs

    @docs.setter
    def docs(self, value: bool):
        self._docs = value
