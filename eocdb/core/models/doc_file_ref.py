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


from ..asserts import assert_not_none
from ..model import Model


class DocFileRef(Model):
    """
    The DocFileRef model.
    """

    def __init__(self,
                 rel_path: str,
                 name: str):
        assert_not_none(rel_path, name='rel_path')
        assert_not_none(name, name='name')
        self._rel_path = rel_path
        self._name = name

    @property
    def rel_path(self) -> str:
        return self._rel_path

    @rel_path.setter
    def rel_path(self, value: rel_path):
        assert_not_none(value, name='value')
        self._rel_path = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        assert_not_none(value, name='value')
        self._name = value
