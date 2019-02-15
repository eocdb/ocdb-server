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


from typing import Dict, List, Optional, Union, Any

from ..asserts import assert_not_none
from ..model import Model


class Dataset(Model):
    Field = Union[str, int, float]

    def __init__(self,
                 metadata: Dict,
                 records: List[List[Field]],
                 id_: str = None,
                 path: str = None):
        assert_not_none(metadata, name='metadata')
        assert_not_none(records, name='records')
        self._id = id_
        self._path = path
        self._metadata = metadata
        self._records = records
        self._longitudes = []
        self._latitudes = []
        self._attributes = []
        self._groups = []
        self._times = []

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: Optional[str]):
        self._id = value

    @property
    def path(self) -> Optional[str]:
        return self._path

    @path.setter
    def path(self, value: Optional[str]):
        self._path = value

    @property
    def metadata(self) -> Dict:
        return self._metadata

    @metadata.setter
    def metadata(self, value: Dict):
        assert_not_none(value, name='value')
        self._metadata = value

    @property
    def records(self) -> List[List[float]]:
        return self._records

    @records.setter
    def records(self, value: List[List[float]]):
        assert_not_none(value, name='value')
        self._records = value

    @property
    def longitudes(self) -> List[float]:
        return self._longitudes

    @longitudes.setter
    def longitudes(self, value: List[float]):
        assert_not_none(value, name='longitudes')
        self._longitudes = value

    @property
    def latitudes(self) -> List[float]:
        return self._latitudes

    @latitudes.setter
    def latitudes(self, value: List[float]):
        assert_not_none(value, name='latitudes')
        self._latitudes = value

    @property
    def attributes(self) -> List[str]:
        return self._attributes

    @attributes.setter
    def attributes(self, value: List[str]):
        assert_not_none(value, name='attributes')
        self._attributes = value

    @property
    def groups(self) -> List[str]:
        return self._groups

    @groups.setter
    def groups(self, value: List[str]):
        self._groups = value

    @property
    def times(self) -> List[str]:
        return self._times

    @times.setter
    def times(self, value: List[str]):
        assert_not_none(value, name='times')
        self._times = value

    def to_dict(self) -> Dict[str, Any]:
        result_dict = super().to_dict()
        converted_times = []
        for time in self._times:
            converted_times.append(time.isoformat())
        result_dict.update({'times': converted_times})
        return result_dict
