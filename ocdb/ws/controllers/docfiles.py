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


from typing import List, Dict

from ..context import WsContext
from ...core.asserts import assert_not_none
from ...core.models.doc_file_ref import DocFileRef


# noinspection PyUnusedLocal
def add_doc_file(ctx: WsContext,
                 data: Dict):
    assert_not_none(data)
    # TODO (generated): implement operation add_doc_file()
    raise NotImplementedError('operation add_doc_file() not yet implemented')


# noinspection PyUnusedLocal
def update_doc_file(ctx: WsContext,
                    data: Dict):
    assert_not_none(data)
    # TODO (generated): implement operation update_doc_file()
    raise NotImplementedError('operation update_doc_file() not yet implemented')


# noinspection PyUnusedLocal,PyTypeChecker
def get_doc_files_in_path(ctx: WsContext,
                          affil: str,
                          project: str,
                          cruise: str) -> List[DocFileRef]:
    assert_not_none(affil, name='affil')
    assert_not_none(project, name='project')
    assert_not_none(cruise, name='cruise')
    # TODO (generated): implement operation get_doc_files_in_bucket()
    raise NotImplementedError('operation get_doc_files_in_bucket() not yet implemented')


# noinspection PyUnusedLocal,PyTypeChecker
def get_doc_file_by_name(ctx: WsContext,
                         affil: str,
                         project: str,
                         cruise: str,
                         name: str) -> bytes:
    assert_not_none(affil, name='affil')
    assert_not_none(project, name='project')
    assert_not_none(cruise, name='cruise')
    assert_not_none(name, name='name')
    # TODO (generated): implement operation download_doc_file()
    raise NotImplementedError('operation download_doc_file() not yet implemented')


# noinspection PyUnusedLocal
def delete_doc_file(ctx: WsContext,
                    affil: str,
                    project: str,
                    cruise: str,
                    name: str):
    assert_not_none(affil, name='affil')
    assert_not_none(project, name='project')
    assert_not_none(cruise, name='cruise')
    assert_not_none(name, name='name')
    # TODO (generated): implement operation delete_doc_file()
    raise NotImplementedError('operation delete_doc_file() not yet implemented')
