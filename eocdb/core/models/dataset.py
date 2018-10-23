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


from typing import Dict, List, Optional, Union

from ..asserts import assert_not_none, assert_one_of
from ..model import Model

DATASET_STATUS_NEW = 'new'
DATASET_STATUS_VALIDATING = 'validating'
DATASET_STATUS_AVAILABLE = 'available'
DATASET_STATUS_HIDDEN = 'hidden'


class Dataset(Model):
    Field = Union[str, int, float]

    """
    The Dataset model.
    """
    def __init__(self,
                 path: str,
                 name: str,
                 status: str,
                 metadata: Dict,
                 records: List[List[Field]],
                 id_: str = None):
        assert_not_none(path, name='path')
        assert_not_none(name, name='name')
        assert_not_none(status, name='status')
        assert_one_of(status, ['new', 'validating', 'available', 'hidden'], name='status')
        assert_not_none(metadata, name='metadata')
        assert_not_none(records, name='records')
        self._id = id_
        self._path = path
        self._name = name
        self._status = status
        self._metadata = metadata
        self._records = records
        self._longitudes = []
        self._latitudes = []

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: Optional[str]):
        self._id = value

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: path):
        assert_not_none(value, name='value')
        self._path = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        assert_not_none(value, name='value')
        self._name = value

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        assert_not_none(value, name='value')
        assert_one_of(value, ['new', 'validating', 'available', 'hidden'], name='value')
        self._status = value

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
