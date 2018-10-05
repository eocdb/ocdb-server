from typing import List

from ._model import Model


class DatasetQuery(Model):

    def __init__(self):
        self._expr = None
        self._region = None
        self._time = None
        self._wdepth = None
        self._mtype = None
        self._shallow = None
        self._pmode = None
        self._pgroup = None
        self._pname = None
        self._offset = None
        self._count = None

    @property
    def expr(self) -> str:
        return self._expr

    @expr.setter
    def expr(self, value: str):
        self._expr = value

    @property
    def region(self) -> List:
        return self._region

    @region.setter
    def region(self, value: List):
        self._region = value

    @property
    def time(self) -> List:
        return self._time

    @time.setter
    def time(self, value: List):
        self._time = value

    @property
    def wdepth(self) -> List:
        return self._wdepth

    @wdepth.setter
    def wdepth(self, value: List):
        self._wdepth = value

    @property
    def mtype(self) -> str:
        return self._mtype

    @mtype.setter
    def mtype(self, value: str):
        self._mtype = value

    @property
    def shallow(self) -> str:
        return self._shallow

    @shallow.setter
    def shallow(self, value: str):
        self._shallow = value

    @property
    def pmode(self) -> str:
        return self._pmode

    @pmode.setter
    def pmode(self, value: str):
        self._pmode = value

    @property
    def pgroup(self) -> List:
        return self._pgroup

    @pgroup.setter
    def pgroup(self, value: List):
        self._pgroup = value

    @property
    def pname(self) -> List:
        return self._pname

    @pname.setter
    def pname(self, value: List):
        self._pname = value

    @property
    def offset(self) -> int:
        return self._offset

    @offset.setter
    def offset(self, value: int):
        self._offset = value

    @property
    def count(self) -> int:
        return self._count

    @count.setter
    def count(self, value: int):
        self._count = value
