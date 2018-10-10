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


from typing import Dict, List

from ..context import WsContext
from ..models.api_response import ApiResponse
from ..models.bucket import Bucket
from ..models.dataset import Dataset
from ..models.dataset_query import DatasetQuery
from ..models.dataset_query_result import DatasetQueryResult
from ..models.dataset_ref import DatasetRef
from ..models.doc_file_ref import DocFileRef
from ..models.user import User


def find_datasets(ctx: WsContext, expr: str = None, region: List[float] = None, time: List[str] = None, wdepth: List[float] = None, mtype: str = None, wlmode: str = None, shallow: str = None, pmode: str = None, pgroup: List[str] = None, pname: List[str] = None, offset: int = None, count: int = None) -> DatasetQueryResult:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation find_datasets() not yet implemented')


def update_dataset(ctx: WsContext, data: Dataset) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation update_dataset() not yet implemented')


def add_dataset(ctx: WsContext, data: Dataset) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation add_dataset() not yet implemented')


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
