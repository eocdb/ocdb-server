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

from eocdb.ws.controllers.store import *
from eocdb.ws.models.api_response import ApiResponse
from ..helpers import new_test_service_context


class StoreTest(unittest.TestCase):

    def setUp(self):
        self.ctx = new_test_service_context()

    def test_get_store_info(self):
        result = get_store_info(self.ctx)
        self.assertIsInstance(result, dict)
        self.assertIn("products", result)
        self.assertIsInstance(result["products"], list)
        self.assertTrue(len(result["products"]) > 300)
        self.assertIn("productGroups", result)
        self.assertIsInstance(result["productGroups"], list)
        self.assertTrue(len(result["productGroups"]) > 15)

    @unittest.skip('not implemented yet')
    def test_upload_store_files(self):
        # TODO: set data dict items
        data = {}

        result = upload_store_files(self.ctx, data=data)
        self.assertIsInstance(result, ApiResponse)
        expected_result = ApiResponse()
        # TODO: set expected result properties
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_download_store_files(self):
        # TODO: set optional parameters
        expr = None
        region = None
        time = None
        wdepth = None
        mtype = None
        wlmode = None
        shallow = None
        pmode = None
        pgroup = None
        pname = None
        docs = None

        result = download_store_files(self.ctx, expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype,
                                      wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname,
                                      docs=docs)
        # TODO: set expected result
        expected_result = None
        self.assertEqual(expected_result, result)
