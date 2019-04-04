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


import unittest

from eocdb.ws.controllers.service import *
from tests.helpers import new_test_service_context


class ServiceTest(unittest.TestCase):

    def setUp(self):
        self.ctx = new_test_service_context()

    def test_get_service_info(self):
        result = get_service_info(self.ctx)
        self.assertIsInstance(result, dict)
        self.assertIn("openapi", result)
        self.assertEqual("3.0.0", result["openapi"])
        self.assertIn("info", result)
        self.assertIsInstance(result["info"], dict)
        self.assertEqual("eocdb-server", result["info"].get("title"))
        self.assertEqual("0.1.0-dev.20", result["info"].get("version"))
        self.assertIsNotNone(result["info"].get("description"))
        self.assertEqual("RESTful API for the EUMETSAT Ocean C",
                         result["info"].get("description")[0:36])
