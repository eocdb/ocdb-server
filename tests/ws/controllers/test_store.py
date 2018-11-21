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
from tests.helpers import new_test_service_context


class StoreTest(unittest.TestCase):

    def setUp(self):
        self.ctx = new_test_service_context()

    def test_get_store_info(self):
        result = get_store_info(self.ctx)
        self.assertIsInstance(result, dict)
        self.assertIn("products", result)
        self.assertIsInstance(result["products"], list)
        self.assertTrue(len(result["products"]) > 300)
        self.assertIsInstance(result["products"][0], dict)
        self.assertIn("productGroups", result)
        self.assertIsInstance(result["productGroups"], list)
        self.assertTrue(len(result["productGroups"]) > 15)
        self.assertIsInstance(result["productGroups"][0], dict)

    def test_upload_store_files(self):
        try:
            data_file_text = ("/begin_header\n"
                              "/received=20120330\n"
                              "/delimiter = comma\n"
                              "/north_latitude=42.598[DEG]\n"
                              "/east_longitude=-67.105[DEG]\n"
                              "/start_date=20101117\n"
                              "/end_date=20101117\n"
                              "/start_time=20:14:00[GMT]\n"
                              "/end_time=20:14:00[GMT]\n"
                              "/fields = station, SN, lat, lon, year, month, day, hour, minute, pressure, wt, sal, CHL, Epar, oxygen\n"
                              "/units = none, none, degrees, degrees, yyyy, mo, dd, hh, mn, dbar, degreesC, PSU, mg/m^3, uE/cm^2s, ml/L\n"
                              "/end_header\n"
                              "97,420,42.598,-67.105,2010,11,17,20,14,3,11.10,33.030,2.47,188,6.1\n")
            uploaded_fie = UploadedFile("DEL1012_Station_097_CTD_Data.txt", "text", data_file_text.encode("utf-8"))

            result = upload_store_files(self.ctx, path="test_files", dataset_files=[uploaded_fie], doc_files=[])
            self.assertEqual([], result["DEL1012_Station_097_CTD_Data.txt"].issues)
            self.assertEqual("OK", result["DEL1012_Station_097_CTD_Data.txt"].status)
        finally:
            target_file = os.path.join(self.ctx.get_datasets_store_path("test_files"), "DEL1012_Station_097_CTD_Data.txt")
            if os.path.isfile(target_file):
                os.remove(target_file)

    @unittest.skip('not implemented yet')
    def test_download_store_files(self):
        # TODO (generated): set optional parameters
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

        # noinspection PyTypeChecker
        result = download_store_files(self.ctx, expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype,
                                      wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname,
                                      docs=docs)
        # TODO (generated): set expected result
        expected_result = None
        self.assertEqual(expected_result, result)
