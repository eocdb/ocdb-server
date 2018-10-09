from .bucket import Bucket
from ..model import Model


class DatasetRef(Model):

    def __init__(self):
        self._id = None
        self._bucket = None
        self._name = None

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
