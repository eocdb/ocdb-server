from typing import List

from ._model import Model


class DocFileRef(Model):

    def __init__(self):
        self._bucket = None
        self._name = None

    @property
    def bucket(self) -> Bucket:
        return self._bucket

    @bucket.setter
    def bucket(self, value: Bucket):
        self._bucket = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
