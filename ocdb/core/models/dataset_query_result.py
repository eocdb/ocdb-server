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

from .dataset_query import DatasetQuery
from .dataset_ref import DatasetRef
from ..asserts import assert_not_none
from ..model import Model


class DatasetQueryResult(Model):
    """
    The DatasetQueryResult model.
    """

    def __init__(self,
                 locations: dict,
                 total_count: int,
                 datasets: List[DatasetRef],
                 query: DatasetQuery):
        assert_not_none(total_count, name='total_count')
        assert_not_none(datasets, name='datasets')
        assert_not_none(query, name='query')
        self._locations = locations
        self._total_count = total_count
        self._datasets = datasets
        self._query = query
        self._dataset_ids = [dataset.id for dataset in datasets]

    @property
    def locations(self) -> dict:
        return self._locations

    @locations.setter
    def locations(self, value: dict):
        assert_not_none(value, name='value')
        self._locations = value

    @property
    def total_count(self) -> int:
        return self._total_count

    @total_count.setter
    def total_count(self, value: int):
        assert_not_none(value, name='value')
        self._total_count = value

    @property
    def datasets(self) -> List[DatasetRef]:
        return self._datasets

    @datasets.setter
    def datasets(self, value: List[DatasetRef]):
        assert_not_none(value, name='value')
        self._datasets = value

    @property
    def query(self) -> DatasetQuery:
        return self._query

    @query.setter
    def query(self, value: DatasetQuery):
        assert_not_none(value, name='value')
        self._query = value

    @property
    def dataset_ids(self) -> List[str]:
        return self._dataset_ids

    @dataset_ids.setter
    def dataset_ids(self, value: List[str]):
        assert_not_none(value, name='value')
        self._dataset_ids = value
