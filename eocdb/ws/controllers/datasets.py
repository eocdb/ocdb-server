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

from ..context import WsContext
from ...core.models.api_response import ApiResponse
from ...core.models.dataset import Dataset
from ...core.models.dataset_query import DatasetQuery
from ...core.models.dataset_query_result import DatasetQueryResult
from ...core.models.dataset_ref import DatasetRef
from ...core.models.dataset_validation_result import DatasetValidationResult


def find_datasets(ctx: WsContext, expr: str = None, region: List[float] = None, time: List[str] = None,
                  wdepth: List[float] = None, mtype: str = None, wlmode: str = None, shallow: str = None,
                  pmode: str = None, pgroup: List[str] = None, pname: List[str] = None, offset: int = None,
                  count: int = None) -> DatasetQueryResult:
    query = DatasetQuery()
    query.expr = expr
    query.region = region
    query.time = time
    query.wdepth = wdepth
    query.mtype = mtype
    query.wlmode = wlmode
    query.shallow = shallow
    query.pmode = pmode
    query.pgroup = pgroup
    query.pname = pname
    query.offset = offset
    query.count = count

    result = DatasetQueryResult()
    result.query = query
    result.datasets = []

    for driver in ctx.get_db_drivers(mode="r"):
        datasets = driver.instance().find_datasets(query)
        if len(datasets) > 0:
            for dataset in datasets:
                dataset_ref = DatasetRef()
                result.datasets.append(dataset_ref)
                result.append(dataset.to_dict())
    return result


def add_dataset(ctx: WsContext, data: Dataset, dry: bool = None) -> DatasetValidationResult:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation add_dataset() not yet implemented')


def update_dataset(ctx: WsContext, data: Dataset, dry: bool = None) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation update_dataset() not yet implemented')


def get_dataset_by_id(ctx: WsContext, id_: str) -> Dataset:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation get_dataset_by_id() not yet implemented')


def delete_dataset(ctx: WsContext, id_: str, api_key: str = None) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation delete_dataset() not yet implemented')


def get_datasets_in_bucket(ctx: WsContext, affil: str, project: str, cruise: str) -> List[DatasetRef]:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation get_datasets_in_bucket() not yet implemented')


def get_dataset_by_bucket_and_name(ctx: WsContext, affil: str, project: str, cruise: str, name: str) -> str:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation get_dataset_by_bucket_and_name() not yet implemented')
