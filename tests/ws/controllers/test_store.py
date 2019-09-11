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

from eocdb.core.db.db_user import DbUser
from eocdb.ws.controllers.store import *
from eocdb.ws.controllers.store import _get_summary_validation_status
from eocdb.ws.controllers.users import create_user
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
        user_id = "77618"
        try:
            data_file_text = ("/begin_header\n"
                              "/investigators=Marks and Spencer\n"
                              "/affiliations=the Institute\n"
                              "/received=20120330\n"
                              "/delimiter = comma\n"
                              "/north_latitude=42.598[DEG]\n"
                              "/south_latitude=42.598[DEG]\n"
                              "/east_longitude=-67.105[DEG]\n"
                              "/west_longitude=-67.105[DEG][DEG]\n"
                              "/start_date=20101117\n"
                              "/end_date=20101117\n"
                              "/start_time=20:14:00[GMT]\n"
                              "/end_time=20:14:00[GMT]\n"
                              "/fields = station, SN, lat, lon, year, month, day, hour, minute, pressure, wt, sal, CHL, Epar, oxygen\n"
                              "/units = none, none, degrees, degrees, yyyy, mo, dd, hh, mn, dbar, degreesC, PSU, mg/m^3, uE/cm^2s, ml/L\n"
                              "/end_header\n"
                              "97,420,42.598,-67.105,2010,11,17,20,14,3,11.10,33.030,2.47,188,6.1\n")
            uploaded_file = UploadedFile("DEL1012_Station_097_CTD_Data.txt", "text", data_file_text.encode("utf-8"))

            result = upload_submission_files(ctx=self.ctx,
                                             path="test_files/cruise/experiment",
                                             submission_id="an_id",
                                             user_id=user_id,
                                             dataset_files=[uploaded_file],
                                             publication_date="2100-01-01",
                                             allow_publication=False,
                                             doc_files=[],
                                             store_sub_path='Tom_Helge')
            self.assertEqual([], result["DEL1012_Station_097_CTD_Data.txt"].issues)
            self.assertEqual("OK", result["DEL1012_Station_097_CTD_Data.txt"].status)
        finally:
            self.delete_test_file("DEL1012_Station_097_CTD_Data.txt")

    def test_upload_store_files_empty_submission_id(self):
        user_id = "77618"
        try:
            data_file_text = ("/begin_header\n"
                              "/investigators=Marks and Spencer\n"
                              "/affiliations=the Institute\n"
                              "/received=20120330\n"
                              "/delimiter = comma\n"
                              "/north_latitude=42.598[DEG]\n"
                              "/south_latitude=42.598[DEG]\n"
                              "/east_longitude=-67.105[DEG]\n"
                              "/west_longitude=-67.105[DEG][DEG]\n"
                              "/start_date=20101117\n"
                              "/end_date=20101117\n"
                              "/start_time=20:14:00[GMT]\n"
                              "/end_time=20:14:00[GMT]\n"
                              "/fields = station, SN, lat, lon, year, month, day, hour, minute, pressure, wt, sal, CHL, Epar, oxygen\n"
                              "/units = none, none, degrees, degrees, yyyy, mo, dd, hh, mn, dbar, degreesC, PSU, mg/m^3, uE/cm^2s, ml/L\n"
                              "/end_header\n"
                              "97,420,42.598,-67.105,2010,11,17,20,14,3,11.10,33.030,2.47,188,6.1\n")
            uploaded_file = UploadedFile("DEL1012_Station_097_CTD_Data.txt", "text", data_file_text.encode("utf-8"))

            with self.assertRaises(WsBadRequestError) as cm:
                upload_submission_files(ctx=self.ctx,
                                        path="test_files",
                                        submission_id="",
                                        user_id=user_id,
                                        dataset_files=[uploaded_file],
                                        publication_date="2100-01-01",
                                        allow_publication=False,
                                        doc_files=[],
                                        store_sub_path='Tom_Helge')

            self.assertEqual("HTTP 400: Submission label is empty!", f"{cm.exception}")

        finally:
            self.delete_test_file("DEL1012_Station_097_CTD_Data.txt")

    def test_upload_store_files_corrupt_file(self):
        user_id = "77618"
        try:
            data_file_text = ("/begin_header\n"
                              "/end_header\n"
                              "97,420,42.598,-67.105,2010,11,17,20,14,3,11.10,33.030,2.47,188,6.1\n")
            uploaded_file = UploadedFile("DEL1012_Station_097_CTD_Data.txt", "text", data_file_text.encode("utf-8"))

            result = upload_submission_files(ctx=self.ctx,
                                             path="test_files/cruise/experiment",
                                             submission_id="an_id",
                                             user_id=user_id,
                                             dataset_files=[uploaded_file],
                                             publication_date="2100-01-01",
                                             allow_publication=False,
                                             doc_files=[],
                                             store_sub_path='Tom_Helge')

            issues = result["DEL1012_Station_097_CTD_Data.txt"].issues
            self.assertEqual(1, len(issues))
            self.assertEqual("ERROR", issues[0].type)
            self.assertEqual('Invalid format: Missing delimiter tag in header', issues[0].description)
            self.assertEqual("ERROR", result["DEL1012_Station_097_CTD_Data.txt"].status)
        finally:
            self.delete_test_file("DEL1012_Station_097_CTD_Data.txt")

    def test_upload_store_files_file_without_header(self):
        user_id = "77618"
        try:
            data_file_text = ("0.99	26.0464	0.055836	36.222\n"
                              "1.99	26.0497	0.0558524	36.2311\n"
                              "2.98	26.0498	0.05586		36.2363")
            uploaded_file = UploadedFile("DEL1012_Station_097_CTD_Data.txt", "text", data_file_text.encode("utf-8"))

            result = upload_submission_files(ctx=self.ctx,
                                             path="test_files/cruise/experiment",
                                             submission_id="an_id",
                                             user_id=user_id,
                                             dataset_files=[uploaded_file],
                                             publication_date="2100-01-01",
                                             allow_publication=False,
                                             doc_files=[],
                                             store_sub_path='Tom_Helge')

            issues = result["DEL1012_Station_097_CTD_Data.txt"].issues
            self.assertEqual(1, len(issues))
            self.assertEqual("ERROR", issues[0].type)
            self.assertEqual('Invalid format: Missing delimiter tag in header', issues[0].description)
            self.assertEqual("ERROR", result["DEL1012_Station_097_CTD_Data.txt"].status)
        finally:
            self.delete_test_file("DEL1012_Station_097_CTD_Data.txt")

    def test_up_and_download_store_files(self):
        try:
            user_id = "77615"
            user = DbUser(id_=user_id, name='scott', password='abc', first_name='Scott', last_name='Tiger',
                          phone='', email='', roles=['submit'])
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

            result = upload_submission_files(ctx=self.ctx,
                                             path="test_files/cruise/experiment",
                                             submission_id="an_id",
                                             user_id=user_id,
                                             dataset_files=[uploaded_file],
                                             publication_date="2100-01-01",
                                             allow_publication=False,
                                             doc_files=[],
                                             store_sub_path='Tom_Helge')
            self.assertEqual([], result["DEL1012_Station_097_CTD_Data.txt"].issues)
            self.assertEqual("OK", result["DEL1012_Station_097_CTD_Data.txt"].status)
        finally:
            self.delete_test_file("DEL1012_Station_097_CTD_Data.txt")

    def test_get_submission(self):
        try:
            user = User(name='scott1', password='abc', first_name='Scott', last_name='Tiger',
                        phone='', email='', roles=[])

            user_id = create_user(ctx=self.ctx, user=user)

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

            upload_submission_files(ctx=self.ctx,
                                    path="test_files/cruise/experiment",
                                    submission_id="an_id",
                                    user_id=user_id,
                                    dataset_files=[uploaded_file],
                                    publication_date="2100-01-01",
                                    allow_publication=False,
                                    doc_files=[],
                                    store_sub_path='Tom_Helge')

            # user_name None and user admin
            user.roles = ['admin']
            result = get_submissions(ctx=self.ctx, user=user, user_name=None)
            self.assertIsNotNone(result)
            self.assertEqual(1, len(result))

            # user_name None and user not admin

            user.roles = ['submit']
            result = get_submissions(ctx=self.ctx, user=user, user_name=None)
            self.assertIsNotNone(result)
            self.assertEqual(0, len(result))

            # user_name exist and user admin

            user.roles = ['admin']
            result = get_submissions(ctx=self.ctx, user=user, user_name="scott1")
            self.assertIsNotNone(result)
            self.assertEqual(1, len(result))

            # user_name exist and user not admin

            user.roles = ['submit']
            result = get_submissions(ctx=self.ctx, user=user, user_name="scott1")
            self.assertIsNotNone(result)
            self.assertEqual(1, len(result))

        finally:
            self.delete_test_file("DEL1012_Station_097_CTD_Data.txt")

    def test_up_and_download_store_files_with_doc_files(self):
        try:
            user = User(name='scott', password='abc', first_name='Scott', last_name='Tiger',
                        phone='', email='', roles=['submit'])

            user_id = create_user(ctx=self.ctx, user=user)

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

            result = upload_submission_files(ctx=self.ctx,
                                             path="test_files/cruise/experiment",
                                             submission_id="an_id",
                                             user_id=user_id,
                                             dataset_files=[uploaded_file],
                                             publication_date="2100-01-01",
                                             allow_publication=False,
                                             doc_files=[document_file],
                                             store_sub_path='Tom_Helge')
            self.assertEqual([], result["DEL1012_Station_097_CTD_Data.txt"].issues)
            self.assertEqual("OK", result["DEL1012_Station_097_CTD_Data.txt"].status)

            result = get_submissions(ctx=self.ctx, user=user, user_name='scott')
            self.assertIsNotNone(result)
            self.assertEqual(1, len(result))
            self.assertEqual("an_id", result[0].submission_id)

            file_refs = result[0].file_refs
            self.assertEqual(2, len(file_refs))

        finally:
            self.delete_test_file("DEL1012_Station_097_CTD_Data.txt")

    def test_upload_and_download_submission_file(self):
        try:
            user_id = "77616"
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

            result = upload_submission_files(ctx=self.ctx,
                                             path="test_files/cruise/experiment",
                                             submission_id="an_id",
                                             user_id=user_id,
                                             dataset_files=[uploaded_file],
                                             publication_date="2100-01-01",
                                             allow_publication=False,
                                             doc_files=[document_file],
                                             store_sub_path='Tom_Helge')
            self.assertEqual([], result["DEL1012_Station_097_CTD_Data.txt"].issues)
            self.assertEqual("OK", result["DEL1012_Station_097_CTD_Data.txt"].status)

            result = get_submission_file(ctx=self.ctx, submission_id="an_id", index=0)
            self.assertIsNotNone(result)
            self.assertEqual("DEL1012_Station_097_CTD_Data.txt", result.filename)

            result = get_submission_file(ctx=self.ctx, submission_id="an_id", index=1)
            self.assertIsNotNone(result)
            self.assertEqual("NSPRT_223_calib.txt", result.filename)

            result = get_submission_file(ctx=self.ctx, submission_id="an_id", index=2)
            self.assertIsNone(result)
        finally:
            self.delete_test_file("DEL1012_Station_097_CTD_Data.txt")

    def test_get_summary_vaidation_status_no_results(self):
        self.assertEqual(DATASET_VALIDATION_RESULT_STATUS_OK, _get_summary_validation_status({}))

    def test_get_summary_vaidation_status_no_errors(self):
        validation_results = {"wilhelm": DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_OK, []),
                              "herta": DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_OK, [])}
        self.assertEqual(DATASET_VALIDATION_RESULT_STATUS_OK, _get_summary_validation_status(validation_results))

    def test_get_summary_vaidation_status_warning(self):
        validation_results = {"wilhelm": DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_OK, []),
                              "herta": DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_WARNING, [])}
        self.assertEqual(DATASET_VALIDATION_RESULT_STATUS_WARNING, _get_summary_validation_status(validation_results))

    def test_get_summary_vaidation_status_error(self):
        validation_results = {"wilhelm": DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_ERROR, []),
                              "herta": DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_OK, [])}
        self.assertEqual(DATASET_VALIDATION_RESULT_STATUS_ERROR, _get_summary_validation_status(validation_results))

    def test_get_summary_vaidation_status_all_mixed(self):
        validation_results = {"wilhelm": DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_ERROR, []),
                              "herta": DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_OK, []),
                              "gerda": DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_WARNING, []),
                              "Fritz": DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_OK, []),
                              "heffalump": DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_OK, [])}
        self.assertEqual(DATASET_VALIDATION_RESULT_STATUS_ERROR, _get_summary_validation_status(validation_results))

    def delete_test_file(self, filename: str):
        target_file = os.path.join(self.ctx.get_datasets_store_path("test_files"),
                                   filename)
        if os.path.isfile(target_file):
            os.remove(target_file)
