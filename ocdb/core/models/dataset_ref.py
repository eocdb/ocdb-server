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


from ..model import Model
from ...core.asserts import assert_not_none


class DatasetRef(Model):
    """
    The DatasetRef model.
    """

    def __init__(self,
                 id_: str,
                 path: str,
                 filename: str):
        assert_not_none(id_, name='id_')
        assert_not_none(path, name='path')
        assert_not_none(filename, name='filename')
        self._id = id_
        self._path = path
        self._filename = filename

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        assert_not_none(value, name='value')
        self._id = value

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str):
        assert_not_none(value, name='value')
        self._path = value

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, value: str):
        assert_not_none(value, name='value')
        self._filename = value