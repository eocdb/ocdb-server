from typing import List

from ._model import Model


class Bucket(Model):

    def __init__(self):
        self._affil = None
        self._project = None
        self._cruise = None

    @property
    def affil(self) -> str:
        return self._affil

    @affil.setter
    def affil(self, value: str):
        self._affil = value

    @property
    def project(self) -> str:
        return self._project

    @project.setter
    def project(self, value: str):
        self._project = value

    @property
    def cruise(self) -> str:
        return self._cruise

    @cruise.setter
    def cruise(self, value: str):
        self._cruise = value
