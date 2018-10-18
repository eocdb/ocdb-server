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


class UploadedFile(Model):
    def __init__(self, filename: str, content_type: str, body: bytes):
        assert_not_none(filename, name="filename")
        assert_not_none(content_type, name="content_type")
        assert_not_none(body, name="body")
        self._filename = filename
        self._content_type = content_type
        self._body = body

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, value: str):
        assert_not_none(value, name="value")
        self._filename = value

    @property
    def content_type(self) -> str:
        return self._content_type

    @content_type.setter
    def content_type(self, value: str):
        assert_not_none(value, name="value")
        self._content_type = value

    @property
    def body(self) -> bytes:
        return self._body

    @body.setter
    def body(self, value: bytes):
        assert_not_none(value, name="value")
        self._body = value
