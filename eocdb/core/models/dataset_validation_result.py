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


from typing import List, Optional

from .issue import Issue
from ..asserts import assert_not_none, assert_one_of
from ..model import Model

DATASET_VALIDATION_RESULT_STATUS_OK = 'OK'
DATASET_VALIDATION_RESULT_STATUS_WARNING = 'WARNING'
DATASET_VALIDATION_RESULT_STATUS_ERROR = 'ERROR'


class DatasetValidationResult(Model):
    """
    The DatasetValidationResult model.
    """

    def __init__(self,
                 status: str,
                 issues: List[Issue]):
        assert_not_none(status, name='status')
        assert_one_of(status, ['OK', 'WARNING', 'ERROR'], name='status')
        assert_not_none(issues, name='issues')
        self._status = status
        self._issues = issues

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        assert_not_none(value, name='value')
        assert_one_of(value, ['OK', 'WARNING', 'ERROR'], name='value')
        self._status = value

    @property
    def issues(self) -> Optional[List[Issue]]:
        return self._issues

    @issues.setter
    def issues(self, value: Optional[List[Issue]]):
        assert_not_none(value, name='value')
        self._issues = value
