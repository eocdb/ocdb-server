# The MIT License (MIT)
# Copyright (c) 2018 by EUMETSAT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import List

from ..model import Model


class DatasetQuery(Model):
    """
    The DatasetQuery model.
    """

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
    def region(self) -> List[float]:
        return self._region

    @region.setter
    def region(self, value: List[float]):
        self._region = value

    @property
    def time(self) -> List[str]:
        return self._time

    @time.setter
    def time(self, value: List[str]):
        self._time = value

    @property
    def wdepth(self) -> List[float]:
        return self._wdepth

    @wdepth.setter
    def wdepth(self, value: List[float]):
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
    def pgroup(self) -> List[str]:
        return self._pgroup

    @pgroup.setter
    def pgroup(self, value: List[str]):
        self._pgroup = value

    @property
    def pname(self) -> List[str]:
        return self._pname

    @pname.setter
    def pname(self, value: List[str]):
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
