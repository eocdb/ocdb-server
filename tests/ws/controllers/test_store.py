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
from zipfile import ZipFile

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
            uploaded_file = UploadedFile("DEL1012_Station_097_CTD_Data.txt", "text", data_file_text.encode("utf-8"))

            result = upload_store_files(self.ctx, path="test_files", dataset_files=[uploaded_file], doc_files=[])
            self.assertEqual([], result["DEL1012_Station_097_CTD_Data.txt"].issues)
            self.assertEqual("OK", result["DEL1012_Station_097_CTD_Data.txt"].status)
        finally:
            self.delete_test_file("DEL1012_Station_097_CTD_Data.txt")

    def test_up_and_download_store_files(self):
        result = None
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
            uploaded_file = UploadedFile("DEL1012_Station_097_CTD_Data.txt", "text", data_file_text.encode("utf-8"))

            result = upload_store_files(self.ctx, path="test_files", dataset_files=[uploaded_file], doc_files=[])
            self.assertEqual([], result["DEL1012_Station_097_CTD_Data.txt"].issues)
            self.assertEqual("OK", result["DEL1012_Station_097_CTD_Data.txt"].status)

            expr = None
            region = [-70, 40, -60, 50]
            time = None
            wdepth = None
            mtype = None
            wlmode = 'all'
            shallow = 'no'
            pmode = 'contains'
            pgroup = None
            pname = None
            docs = None

            # noinspection PyTypeChecker
            result = download_store_files(self.ctx, expr=expr, region=region, s_time=time, wdepth=wdepth, mtype=mtype,
                                          wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname,
                                          docs=docs)

            self.assertIsNotNone(result)
            self.assertTrue(isinstance(result, ZipFile))
            info_list = result.infolist()
            self.assertEqual(1, len(info_list))
            self.assertEqual("test_files/archive/DEL1012_Station_097_CTD_Data.txt", info_list[0].filename)

        finally:
            self.delete_test_file("DEL1012_Station_097_CTD_Data.txt")

            tmp_dir = tempfile.gettempdir()
            if result is not None:
                zip_file_path = os.path.join(tmp_dir, result.filename)
                if os.path.isfile(zip_file_path):
                    os.remove(zip_file_path)

    def test_up_and_download_store_files_with_doc_files(self):
        result = None
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
                              "/documents=NSPRT_223_calib.txt\n"
                              "/fields = station, SN, lat, lon, year, month, day, hour, minute, pressure, wt, sal, CHL, Epar, oxygen\n"
                              "/units = none, none, degrees, degrees, yyyy, mo, dd, hh, mn, dbar, degreesC, PSU, mg/m^3, uE/cm^2s, ml/L\n"
                              "/end_header\n"
                              "97,420,42.598,-67.105,2010,11,17,20,14,3,11.10,33.030,2.47,188,6.1\n")
            uploaded_file = UploadedFile("DEL1012_Station_097_CTD_Data.txt", "text", data_file_text.encode("utf-8"))

            document_file_content = "This is test content and does not reflect the opinion of the development team."
            document_file = UploadedFile("NSPRT_223_calib.txt", "text", document_file_content.encode("utf-8"))

            result = upload_store_files(self.ctx, path="test_files", dataset_files=[uploaded_file],
                                        doc_files=[document_file])
            self.assertEqual([], result["DEL1012_Station_097_CTD_Data.txt"].issues)
            self.assertEqual("OK", result["DEL1012_Station_097_CTD_Data.txt"].status)

            expr = None
            region = [-70, 40, -60, 50]
            time = None
            wdepth = None
            mtype = None
            wlmode = 'all'
            shallow = 'no'
            pmode = 'contains'
            pgroup = None
            pname = None
            docs = True

            # noinspection PyTypeChecker
            result = download_store_files(self.ctx, expr=expr, region=region, s_time=time, wdepth=wdepth, mtype=mtype,
                                          wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname,
                                          docs=docs)

            self.assertIsNotNone(result)
            self.assertTrue(isinstance(result, ZipFile))
            info_list = result.infolist()
            self.assertEqual(2, len(info_list))
            self.assertEqual("test_files/archive/DEL1012_Station_097_CTD_Data.txt", info_list[0].filename)
            self.assertEqual("test_files/documents/NSPRT_223_calib.txt", info_list[1].filename)

        finally:
            self.delete_test_file("DEL1012_Station_097_CTD_Data.txt")

            if result is not None:
                tmp_dir = tempfile.gettempdir()
                zip_file_path = os.path.join(tmp_dir, result.filename)
                if os.path.isfile(zip_file_path):
                    os.remove(zip_file_path)

    def test_up_and_download_store_files_by_id_list(self):
        result = None
        try:
            data_file_text = ("/begin_header\n"
                              "/delimiter = tab\n"
                              "/north_latitude=54.0859[DEG]\n"
                              "/east_longitude=-35.7178[DEG]\n"
                              "/start_date=20151108\n"
                              "/end_date=20151130\n"
                              "/start_time=03:09:02[GMT]\n"
                              "/end_time=01:18:23[GMT]\n"
                              "/fields=date,time,lat,lon,SST,sal,F-initial,Fm,Fv_Fm,Sigma_PSII,PAR\n"
                              "/units=yyyymmdd,hh:mm:ss,degrees,degrees,degreesC,PSU,unitless,unitless,unitless,angstrom^2,uE/cm^2/s\n"
                              "/end_header\n"
                              "20151108	03:09:02	42.39	-62.92	15.836	33.404	44.802	71.669	0.375	921.720	0\n"
                              "20151108	03:12:11	42.39	-62.91	15.815	33.397	44.533	72.709	0.388	910.600	0\n")
            uploaded_fie = UploadedFile("Campaign01_FRR_PAR_SST_SAL.txt", "text", data_file_text.encode("utf-8"))

            result = upload_store_files(self.ctx, path="test_files", dataset_files=[uploaded_fie], doc_files=[])
            self.assertEqual([], result["Campaign01_FRR_PAR_SST_SAL.txt"].issues)
            self.assertEqual("OK", result["Campaign01_FRR_PAR_SST_SAL.txt"].status)

            data_file_text = ("/begin_header\n"
                              "/delimiter = comma\n"
                              "/north_latitude=33.077[DEG]\n"
                              "/east_longitude=-78.211[DEG]\n"
                              "/start_date=20151212\n"
                              "/end_date=20151212\n"
                              "/start_time=20:22:07[GMT]\n"
                              "/end_time=20:22:07[GMT]\n"
                              "/fields=nadir,relaz,Lu436/Lu436(nadir),Lu436/Lu436(nadir)_CV\n"
                              "/units=degrees,degrees,dimensionless,dimensionless\n"
                              "/end_header\n"
                              "0,0,1.00E+00,1.68E-02\n"
                              "5,0,9.88E-01,1.65E-02\n")
            uploaded_fie = UploadedFile("d25b1.002", "text", data_file_text.encode("utf-8"))

            result = upload_store_files(self.ctx, path="test_files", dataset_files=[uploaded_fie], doc_files=[])
            self.assertEqual([], result["d25b1.002"].issues)
            self.assertEqual("OK", result["d25b1.002"].status)

            # we need to make some effort to fetch the dataset ids from here tb 2019-02-01
            query_result = self.ctx.db_driver.find_datasets(DatasetQuery())
            self.assertEqual(2, len(query_result.datasets))
            id_list = []
            for dataset in query_result.datasets:
                id_list.append(dataset.id)


            # noinspection PyTypeChecker
            result = download_store_files_by_id(self.ctx, dataset_ids=id_list)

            self.assertIsNotNone(result)
            self.assertTrue(isinstance(result, ZipFile))
            info_list = result.infolist()
            self.assertEqual(2, len(info_list))
            self.assertEqual("test_files/archive/Campaign01_FRR_PAR_SST_SAL.txt", info_list[0].filename)
            self.assertEqual("test_files/archive/d25b1.002", info_list[1].filename)

        finally:
            self.delete_test_file("Campaign01_FRR_PAR_SST_SAL.txt")
            self.delete_test_file("d25b1.002")

            tmp_dir = tempfile.gettempdir()
            if result is not None:
                zip_file_path = os.path.join(tmp_dir, result.filename)
                if os.path.isfile(zip_file_path):
                    os.remove(zip_file_path)

    def delete_test_file(self, filename: str):
        target_file = os.path.join(self.ctx.get_datasets_store_path("test_files"),
                                   filename)
        if os.path.isfile(target_file):
            os.remove(target_file)