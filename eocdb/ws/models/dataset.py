from typing import List

from ._model import Model


class Dataset(Model):

    def __init__(self):
        self._id = None
        self._bucket = None
        self._name = None
        self._status = None
        self._header = None
        self._records = None

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

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

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        self._status = value

    @property
    def header(self) -> object:
        return self._header

    @header.setter
    def header(self, value: object):
        self._header = value

    @property
    def records(self) -> object:
        return self._records

    @records.setter
    def records(self, value: object):
        self._records = value
