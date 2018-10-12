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
from ...db.static_data import get_product_groups, get_products


def get_store_info(ctx: WsContext) -> Dict:
    return dict(products=get_products(), productGroups=get_product_groups())


def upload_store_files(ctx: WsContext, data: Dict) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation upload_store_files() not yet implemented')


def download_store_files(ctx: WsContext, expr: str = None, region: List[float] = None, time: List[str] = None,
                         wdepth: List[float] = None, mtype: str = None, wlmode: str = None, shallow: str = None,
                         pmode: str = None, pgroup: List[str] = None, pname: List[str] = None,
                         docs: bool = None) -> str:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation download_store_files() not yet implemented')
