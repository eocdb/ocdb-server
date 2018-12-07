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


from typing import List, Optional

from ..model import Model


class DatasetQuery(Model):
    """
    The DatasetQuery model.
    """

    def __init__(self,
                 expr: str = None,
                 region: List[float] = None,
                 time: List[str] = None,
                 wdepth: List[float] = None,
                 mtype: str = 'all',
                 shallow: str = None,
                 pmode: str = 'all',
                 pgroup: List[str] = None,
                 pname: List[str] = None,
                 geojson: bool=False,
                 offset: int = 1,
                 count: int = 1000):
        self._expr = expr
        self._region = region
        self._time = time
        self._wdepth = wdepth
        self._mtype = mtype
        self._shallow = shallow
        self._pmode = pmode
        self._pgroup = pgroup
        self._pname = pname
        self._geojson = geojson
        self._offset = offset
        self._count = count

    @property
    def expr(self) -> Optional[str]:
        return self._expr

    @expr.setter
    def expr(self, value: Optional[str]):
        self._expr = value

    @property
    def region(self) -> Optional[List[float]]:
        return self._region

    @region.setter
    def region(self, value: Optional[List[float]]):
        self._region = value

    @property
    def time(self) -> Optional[List[str]]:
        return self._time

    @time.setter
    def time(self, value: Optional[List[str]]):
        self._time = value

    @property
    def wdepth(self) -> Optional[List[float]]:
        return self._wdepth

    @wdepth.setter
    def wdepth(self, value: Optional[List[float]]):
        self._wdepth = value

    @property
    def mtype(self) -> Optional[str]:
        return self._mtype

    @mtype.setter
    def mtype(self, value: Optional[str]):
        self._mtype = value

    @property
    def shallow(self) -> Optional[str]:
        return self._shallow

    @shallow.setter
    def shallow(self, value: Optional[str]):
        self._shallow = value

    @property
    def pmode(self) -> Optional[str]:
        return self._pmode

    @pmode.setter
    def pmode(self, value: Optional[str]):
        self._pmode = value

    @property
    def pgroup(self) -> Optional[List[str]]:
        return self._pgroup

    @pgroup.setter
    def pgroup(self, value: Optional[List[str]]):
        self._pgroup = value

    @property
    def pname(self) -> Optional[List[str]]:
        return self._pname

    @pname.setter
    def pname(self, value: Optional[List[str]]):
        self._pname = value

    @property
    def geojson(self) -> bool:
        return self._geojson

    @geojson.setter
    def geojson(self, value: bool):
        self._geojson = value

    @property
    def offset(self) -> Optional[int]:
        return self._offset

    @offset.setter
    def offset(self, value: Optional[int]):
        self._offset = value

    @property
    def count(self) -> Optional[int]:
        return self._count

    @count.setter
    def count(self, value: Optional[int]):
        self._count = value
