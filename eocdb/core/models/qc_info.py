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


from typing import Dict, Optional

from ..model import Model
from ...core.asserts import assert_not_none, assert_one_of

QC_STATUS_SUBMITTED = 'SUBMITTED'
QC_STATUS_VALIDATED = 'VALIDATED'
QC_STATUS_APPROVED = 'APPROVED'
QC_STATUS_PUBLISHED = 'PUBLISHED'


class QcInfo(Model):
    """
    The QcInfo model.
    """

    def __init__(self,
                 status: str,
                 result: Dict = None):
        assert_not_none(status, name='status')
        assert_one_of(status, [QC_STATUS_SUBMITTED, QC_STATUS_VALIDATED, QC_STATUS_APPROVED, QC_STATUS_PUBLISHED], name='status')
        self._status = status
        self._result = result

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        assert_not_none(value, name='value')
        assert_one_of(value, [QC_STATUS_SUBMITTED, QC_STATUS_VALIDATED, QC_STATUS_APPROVED, QC_STATUS_PUBLISHED], name='value')
        self._status = value

    @property
    def result(self) -> Optional[Dict]:
        return self._result

    @result.setter
    def result(self, value: Optional[Dict]):
        self._result = value
