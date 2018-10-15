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


class Bucket(Model):
    """
    The Bucket model.
    """

    def __init__(self,
                 affil: str,
                 project: str,
                 cruise: str):
        assert_not_none(affil, name='affil')
        assert_not_none(project, name='project')
        assert_not_none(cruise, name='cruise')
        self._affil = affil
        self._project = project
        self._cruise = cruise

    @property
    def affil(self) -> str:
        return self._affil

    @affil.setter
    def affil(self, value: str):
        assert_not_none(value, name='value')
        self._affil = value

    @property
    def project(self) -> str:
        return self._project

    @project.setter
    def project(self, value: str):
        assert_not_none(value, name='value')
        self._project = value

    @property
    def cruise(self) -> str:
        return self._cruise

    @cruise.setter
    def cruise(self, value: str):
        assert_not_none(value, name='value')
        self._cruise = value
