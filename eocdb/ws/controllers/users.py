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


def create_user(ctx: WsContext, data: User) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation create_user() not yet implemented')


def login_user(ctx: WsContext, username: str = None, password: str = None) -> str:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation login_user() not yet implemented')


def logout_user(ctx: WsContext) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation logout_user() not yet implemented')


def get_user_by_id(ctx: WsContext, id_: int) -> User:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation get_user_by_id() not yet implemented')


def update_user(ctx: WsContext, id_: int, data: User) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation update_user() not yet implemented')


def delete_user(ctx: WsContext, id_: int) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation delete_user() not yet implemented')
