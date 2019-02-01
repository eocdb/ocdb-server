from typing import List

from ..model import Model


class DatasetIds(Model):

    def __init__(self, ids: List[str]):
        self._id_list = ids

    @property
    def id_list(self) -> List[str]:
        return self._id_list
