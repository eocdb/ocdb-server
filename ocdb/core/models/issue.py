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


from ..asserts import assert_not_none, assert_one_of
from ..model import Model

ISSUE_TYPE_WARNING = 'WARNING'
ISSUE_TYPE_ERROR = 'ERROR'


class Issue(Model):
    """
    The Issue model.
    """

    def __init__(self,
                 type: str,
                 description: str):
        assert_not_none(type, name='type_')
        assert_one_of(type, ['WARNING', 'ERROR'], name='type_')
        assert_not_none(description, name='description')
        self._type = type
        self._description = description

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str):
        assert_not_none(value, name='value')
        assert_one_of(value, ['WARNING', 'ERROR'], name='value')
        self._type = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        assert_not_none(value, name='value')
        self._description = value
