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
import datetime
import io
import os
import unittest
import urllib.parse
import zipfile

import tornado.escape
import tornado.testing

from eocdb.core.db.db_submission import DbSubmission
from eocdb.core.models import DatasetValidationResult, Issue
from eocdb.core.models.qc_info import QcInfo, QC_STATUS_SUBMITTED, \
    QC_STATUS_VALIDATED, QC_STATUS_APPROVED
from eocdb.core.models.submission import Submission, TYPE_MEASUREMENT
from eocdb.core.models.submission_file import SubmissionFile
from eocdb.ws.app import new_application
from eocdb.ws.controllers.datasets import add_dataset, find_datasets, get_dataset_by_id_strict, get_dataset_qc_info
from eocdb.ws.handlers import API_URL_PREFIX
from eocdb.ws.handlers._handlers import _ensure_string_argument, WsBadRequestError, _ensure_int_argument, \
    StoreStatusSubmission
from tests.core.mpf import MultiPartForm
from tests.helpers import new_test_service_context, new_test_dataset


class WsTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        """Implements AsyncHTTPTestCase.get_app()."""
        application = new_application()
        application.ws_context = new_test_service_context()
        return application

    @property
    def ctx(self):
        return self._app.ws_context


class ServiceInfoTest(WsTestCase):

    def test_get(self):
        response = self.fetch(API_URL_PREFIX + "/service/info", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        result = tornado.escape.json_decode(response.body)
        self.assertIn("openapi", result)
        self.assertEqual("3.0.0", result["openapi"])
        self.assertIn("info", result)
        self.assertIsInstance(result["info"], dict)
        self.assertEqual("eocdb-server", result["info"].get("title"))
        self.assertEqual("0.1.0-dev.20", result["info"].get("version"))
        self.assertIsNotNone(result["info"].get("description"))
        self.assertEqual("RESTful API for the EUMETSAT Ocean C",
                         result["info"].get("description")[0:36])


class StoreInfoTest(WsTestCase):

    def test_get(self):
        response = self.fetch(API_URL_PREFIX + "/store/info", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        result = tornado.escape.json_decode(response.body)
        self.assertIsInstance(result, dict)
        self.assertIn("products", result)
        self.assertIn("productGroups", result)


class StoreUploadSubmissionTest(WsTestCase):

    def test_post_invalid_submission_id(self):
        mpf = MultiPartForm(boundary="HEFFALUMP")
        mpf.add_field("submissionid", "")

        response = self.fetch(API_URL_PREFIX + "/store/upload/submission", method='POST', body=bytes(mpf))
        self.assertEqual(400, response.code)
        self.assertEqual("Invalid argument 'submissionid' in body: None", response.reason)

    def test_post_submission_id_already_present(self):
        submission_id = "I_DO_EXIST"
        submission = Submission(submission_id=submission_id,
                                user_id=12,
                                date=datetime.datetime.now(),
                                status="who_knows",
                                qc_status="OK",
                                publication_date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                allow_publication=False,
                                file_refs=[])
        self.ctx.db_driver.add_submission(submission)

        mpf = MultiPartForm(boundary="HEFFALUMP")
        mpf.add_field("submissionid", submission_id)

        response = self.fetch(API_URL_PREFIX + "/store/upload/submission", method='POST', body=bytes(mpf))
        self.assertEqual(400, response.code)
        self.assertEqual("Invalid argument 'submissionid' in body: None", response.reason)

    def test_delete_invalid_id(self):
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/ABCDEFGHI", method='DELETE')

        self.assertEqual(404, response.code)
        self.assertEqual('Submission not found', response.reason)

    def test_delete_success(self):
        submission_id = "I_DO_EXIST"
        submission = DbSubmission(submission_id=submission_id,
                                  user_id=12,
                                  date=datetime.datetime.now(),
                                  status="who_knows",
                                  qc_status="OK",
                                  path="temp",
                                  publication_date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                  allow_publication=False,
                                  files=[])
        self.ctx.db_driver.add_submission(submission)

        response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/I_DO_EXIST", method='DELETE')

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

    def test_get_invalid_id(self):
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/ABCDEFGHI", method='GET')

        self.assertEqual(404, response.code)
        self.assertEqual('Submission not found', response.reason)

    def test_get_success(self):
        submission_id = "I_DO_EXIST"
        submission = DbSubmission(submission_id=submission_id,
                                  user_id=12,
                                  date=datetime.datetime.now(),
                                  status="who_knows",
                                  qc_status="OK",
                                  path="temp",
                                  publication_date='2001-02-03T04:05:06',
                                  allow_publication=False,
                                  files=[])
        self.ctx.db_driver.add_submission(submission)

        response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/I_DO_EXIST", method='GET')

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        del actual_response_data["date"]    # varies, therefore we do not check tb 2019-03-13
        del actual_response_data["id"]    # varies, therefore we do not check tb 2019-03-13
        self.assertEqual({
            'file_refs': [],
            'files': [],
            'path': 'temp',
            'publication_date': '2001-02-03T04:05:06',
            'allow_publication': False,
            'qc_status': 'OK',
            'status': 'who_knows',
            'submission_id': 'I_DO_EXIST',
            'user_id': 12}, actual_response_data)


class StoreStatusSubmissionTest(WsTestCase):

    def test_put_invalid_id(self):
        body = tornado.escape.json_encode({"status": QC_STATUS_APPROVED, "date": "20170822"})
        response = self.fetch(API_URL_PREFIX + f"/store/status/submission/abcdefghijick", body=body, method='PUT')

        self.assertEqual(404, response.code)
        self.assertEqual('Submission not found', response.reason)

    def test_put_approve(self):
        submission_id = "I_DO_EXIST"
        submission = DbSubmission(submission_id=submission_id,
                                  user_id=12,
                                  date=datetime.datetime.now(),
                                  status=QC_STATUS_VALIDATED,
                                  qc_status="OK",
                                  path="temp",
                                  publication_date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                  allow_publication=False,
                                  files=[])
        self.ctx.db_driver.add_submission(submission)

        body = tornado.escape.json_encode({"status": QC_STATUS_APPROVED,
                                           "date": "20180923",
                                           'publication_date': '20180923',
                                           'allow_publication': False,
                                           })
        response = self.fetch(API_URL_PREFIX + f"/store/status/submission/{submission_id}", body=body, method='PUT')

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/{submission_id}",  method='GET')

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        del actual_response_data["date"]  # varies, therefore we do not check tb 2019-03-13
        del actual_response_data["id"]  # varies, therefore we do not check tb 2019-03-13
        self.assertEqual({
            'file_refs': [],
            'files': [],
            'path': 'temp',
            'qc_status': 'OK',

            'status': QC_STATUS_APPROVED,
            'submission_id': 'I_DO_EXIST',
            'publication_date': None, #!!! Comes in here as None. Should ba a date.!! Need to check
            'allow_publication': False,
            'user_id': 12}, actual_response_data)

    def test_extract_date_not_present(self):
        body_dict = {"status": "whatever"}

        date = StoreStatusSubmission._extract_date(body_dict)
        self.assertIsNone(date)

    def test_extract_date(self):
        body_dict = {"status": "whatever", "date": "20180317"}

        date = StoreStatusSubmission._extract_date(body_dict)
        self.assertIsNotNone(date)
        self.assertEqual(2018, date.tm_year)
        self.assertEqual(3, date.tm_mon)
        self.assertEqual(17, date.tm_mday)


class StoreUploadSubmissionFileTest(WsTestCase):

    def test_get_no_results(self):
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/ABCDEFGHI/0", method='GET')

        self.assertEqual(400, response.code)
        self.assertEqual('No result found', response.reason)

    def test_get_one_result(self):
        # --- add submission file ---
        files = [SubmissionFile(submission_id="submitme",
                                index=0,
                                filename="Hans",
                                filetype="black",
                                status=QC_STATUS_SUBMITTED,
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id="submitme",
                                index=1,
                                filename="Helga",
                                filetype="green",
                                status=QC_STATUS_VALIDATED,
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]
        db_subm = DbSubmission(status="Hellyeah", user_id=88763, submission_id="submitme", files=files, qc_status="OK",
                               path="/root/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                               publication_date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                               allow_publication=False)
        self.ctx.db_driver.add_submission(db_subm)

        # --- get submission file ---
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/submitme/0", method='GET')

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual({'filename': 'Hans',
                          'filetype': 'black',
                          'index': 0,
                          'result': {'issues': [], 'status': 'OK'},
                          'status': QC_STATUS_SUBMITTED,
                          'submission_id': 'submitme'}, actual_response_data)

    def test_delete_no_submissions(self):
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/ABCDEFGHI/0", method='DELETE')

        self.assertEqual(404, response.code)
        self.assertEqual('Submission not found', response.reason)

    def test_delete(self):
        files = [SubmissionFile(submission_id="submitme",
                                index=0,
                                filename="Hans",
                                filetype="black",
                                status=QC_STATUS_SUBMITTED,
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id="submitme",
                                index=1,
                                filename="Helga",
                                filetype="green",
                                status=QC_STATUS_VALIDATED,
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]
        db_subm = DbSubmission(status="Hellyeah", user_id=88763, submission_id="submitme", files=files, qc_status="OK",
                               path="/root/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                               publication_date='2001-02-03T04:05:06',
                               allow_publication=False)
        self.ctx.db_driver.add_submission(db_subm)

        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/submitme/0", method='DELETE')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        userid = 88763
        response = self.fetch(API_URL_PREFIX + f"/store/upload/user/{userid}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual([{'date': '2001-02-03T04:05:06',
                           'file_refs': [{'filename': 'Helga',
                                          'filetype': 'green',
                                          'index': 0,
                                          'status': 'VALIDATED',
                                          'submission_id': 'submitme'}],
                           'qc_status': 'OK',
                           'status': 'Hellyeah',
                           'submission_id': 'submitme',
                           'publication_date': '2001-02-03T04:05:06',
                           'allow_publication': False,
                           'user_id': 88763}], actual_response_data)

    def test_put_invalid_submissionid(self):
        submissionid = "rattelschneck"
        mpf = MultiPartForm(boundary="HEFFALUMP")
        mpf.add_field("submissionid", submissionid)
        index = 0
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/{submissionid}/{index}", method='PUT',
                              body=bytes(mpf))

        self.assertEqual(404, response.code)
        self.assertEqual('Submission not found', response.reason)

    def test_put_no_body(self):
        submissionid = "rattelschneck"
        files = [SubmissionFile(submission_id=submissionid,
                                index=0,
                                filename="Hans",
                                filetype="black",
                                status=QC_STATUS_SUBMITTED,
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id=submissionid,
                                index=1,
                                filename="Helga",
                                filetype="green",
                                status=QC_STATUS_VALIDATED,
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]
        db_subm = DbSubmission(status="Hellyeah", user_id=88763, submission_id=submissionid, files=files,
                               qc_status="OK",
                               path="/root/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6))
        self.ctx.db_driver.add_submission(db_subm)

        mpf = MultiPartForm(boundary="HEFFALUMP")
        mpf.add_field("submissionid", submissionid)
        index = 0
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/{submissionid}/{index}", method='PUT',
                              body=bytes(mpf), headers={"Content-Type": mpf.content_type})

        self.assertEqual(400, response.code)
        self.assertEqual('Invalid number of files supplied', response.reason)

    def test_put_invalid_index(self):
        submissionid = "rattelschneck"
        files = [SubmissionFile(submission_id=submissionid,
                                index=0,
                                filename="Hans",
                                filetype="black",
                                status=QC_STATUS_SUBMITTED,
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id=submissionid,
                                index=1,
                                filename="Helga",
                                filetype="green",
                                status=QC_STATUS_VALIDATED,
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]
        db_subm = DbSubmission(status="Hellyeah", user_id=88763, submission_id=submissionid, files=files,
                               qc_status="OK",
                               path="/root/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6))
        self.ctx.db_driver.add_submission(db_subm)

        index = -2
        mpf = MultiPartForm(boundary="HEFFALUMP")
        mpf.add_field("submissionid", submissionid)
        dataset = self._create_valid_dataset()
        mpf.add_file(f'datasetfiles', "the_uploaded_file.sb", io.StringIO(dataset), mime_type="text/plain")
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/{submissionid}/{index}", method='PUT',
                              body=bytes(mpf), headers={"Content-Type": mpf.content_type})

        self.assertEqual(400, response.code)
        self.assertEqual('Invalid submission file index', response.reason)

    def test_put_success(self):
        submissionid = "rabatz"
        files = [SubmissionFile(submission_id=submissionid,
                                index=0,
                                filename="Hans",
                                filetype="black",
                                status=QC_STATUS_SUBMITTED,
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id=submissionid,
                                index=1,
                                filename="Helga",
                                filetype="green",
                                status=QC_STATUS_VALIDATED,
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]
        db_subm = DbSubmission(status="Hellyeah", user_id=88763, submission_id=submissionid, files=files,
                               qc_status="OK",
                               path="/tmp/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6))
        self.ctx.db_driver.add_submission(db_subm)

        index = 1
        mpf = MultiPartForm(boundary="HEFFALUMP")
        mpf.add_field("submissionid", submissionid)
        dataset = self._create_valid_dataset()
        mpf.add_file(f'datasetfiles', "the_uploaded_file.sb", io.StringIO(dataset), mime_type="text/plain")
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/{submissionid}/{index}", method='PUT',
                              body=bytes(mpf), headers={"Content-Type": mpf.content_type})

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/{submissionid}/{index}", method='GET')

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual({'filename': 'the_uploaded_file.sb',
                          'filetype': TYPE_MEASUREMENT,
                          'index': 1,
                          'result': {'issues': [], 'status': 'OK'},
                          'status': QC_STATUS_VALIDATED,
                          'submission_id': 'rabatz'}, actual_response_data)

    @staticmethod
    def _create_valid_dataset() -> str:
        return "/begin_header\n" \
               "/investigators=Frank_Muller-Karger,Enrique_Montes\n" \
               "/affiliations=University_of_South_Florida,USA\n" \
               "/contact=emontesh@mail.usf.edu\n" \
               "/experiment=SFP\n" \
               "/cruise=WS15320\n" \
               "/data_file_name=WS15320_1_ap_ad\n" \
               "/documents=WS_cruises_report.pdf\n" \
               "/calibration_files=CalReport_SPECTRIX_USF_Hu\n" \
               "/data_type=scan\n" \
               "/water_depth=-999\n" \
               "/missing=-999\n" \
               "/delimiter=space\n" \
               "/fields=wavelength,abs_ap,ap,abs_ad,ad\n" \
               "/units=nm,unitless,1/m,unitless,1/m\n" \
               "/north_latitude=25.010[DEG]\n" \
               "/south_latitude=25.010[DEG]\n" \
               "/east_longitude=-80.380[DEG]\n" \
               "/west_longitude=-80.380[DEG]\n" \
               "/start_time=21:18:00[GMT]\n" \
               "/end_time=21:18:00[GMT]\n" \
               "/start_date=20151116\n" \
               "/end_date=20151116\n" \
               "/end_header\n" \
               "400 0.120725 0.018486 0.059251 0.00714\n" \
               "401  0.121268  0.018595  0.058999  0.007099"


class StoreUpdateSubmissionFileTest(WsTestCase):

    def test_update_invalid_submissionfile(self):
        submission_id = "not_stored"
        index = 8
        status = QC_STATUS_VALIDATED
        response = self.fetch(API_URL_PREFIX + f"/store/status/submissionfile/{submission_id}/{index}/{status}",
                              method='GET')

        self.assertEqual(404, response.code)
        self.assertEqual('Submission not found', response.reason)

    def test_update_invalid_index(self):
        files = [SubmissionFile(submission_id="submitme",
                                index=0,
                                filename="Hans",
                                filetype="black",
                                status=QC_STATUS_SUBMITTED,
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id="submitme",
                                index=1,
                                filename="Helga",
                                filetype="green",
                                status=QC_STATUS_VALIDATED,
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]
        db_subm = DbSubmission(status="Hellyeah", user_id=88763, submission_id="submitme", files=files, qc_status="OK",
                               path="/root/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6))
        self.ctx.db_driver.add_submission(db_subm)

        submission_id = "submitme"
        index = 8
        status = QC_STATUS_APPROVED
        response = self.fetch(API_URL_PREFIX + f"/store/status/submissionfile/{submission_id}/{index}/{status}",
                              method='GET')

        self.assertEqual(400, response.code)
        self.assertEqual('Invalid submission file index', response.reason)

    def test_update_success(self):
        files = [SubmissionFile(submission_id="submitme",
                                index=0,
                                filename="Hans",
                                filetype="black",
                                status=QC_STATUS_SUBMITTED,
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id="submitme",
                                index=1,
                                filename="Helga",
                                filetype="green",
                                status=QC_STATUS_VALIDATED,
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]
        db_subm = DbSubmission(status="Hellyeah", user_id=88763, submission_id="submitme", files=files, qc_status="OK",
                               path="/root/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6))
        self.ctx.db_driver.add_submission(db_subm)

        submission_id = "submitme"
        index = 1
        status = QC_STATUS_APPROVED
        response = self.fetch(API_URL_PREFIX + f"/store/status/submissionfile/{submission_id}/{index}/{status}",
                              method='GET')

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/submitme/1", method='GET')

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual({'filename': 'Helga',
                          'filetype': 'green',
                          'index': 1,
                          'result': {'issues': [{'description': 'This might be wrong',
                                                 'type': 'WARNING'}],
                                     'status': 'WARNING'},
                          'status': 'APPROVED',
                          'submission_id': 'submitme'}, actual_response_data)


class StoreUploadUserTest(WsTestCase):

    def test_get_no_results(self):
        userid = 227654487
        response = self.fetch(API_URL_PREFIX + f"/store/upload/user/{userid}", method='GET')

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        expected_response_data = []
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)


class StoreDownloadTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_get(self):
        # TODO (generated): set query parameter(s) to reasonable value(s)
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
        geojson = False
        query = urllib.parse.urlencode(
            dict(expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype, wlmode=wlmode, shallow=shallow,
                 pmode=pmode, pgroup=pgroup, pname=pname, docs=docs, geojson=geojson))

        response = self.fetch(API_URL_PREFIX + f"/store/download?{query}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = None
        actual_response_data = response.body
        self.assertEqual(expected_response_data, actual_response_data)

    def test_post_empty_list(self):
        id_dict = {"id_list": [], "docs": False}
        body = tornado.escape.json_encode(id_dict)
        response = self.fetch(API_URL_PREFIX + "/store/download", method='POST', body=body)

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        self.assertIsNone(response._body)

    def test_post_valid_list(self):
        target_dir = None
        target_file_1 = None
        target_file_2 = None
        try:
            target_dir = os.path.join(self.ctx.store_path, "archive")
            os.makedirs(target_dir)

            ds_ref_1 = add_dataset(self.ctx, new_test_dataset(0))
            target_file_1 = os.path.join(self.ctx.store_path, ds_ref_1.path)
            with open(target_file_1, "w") as fp:
                fp.write("firlefanz")

            ds_ref_2 = add_dataset(self.ctx, new_test_dataset(1))
            target_file_2 = os.path.join(self.ctx.store_path, ds_ref_2.path)
            with open(target_file_2, "w") as fp:
                fp.write("schnickschnack")

            id_dict = {"id_list": [ds_ref_1.id, ds_ref_2.id], "docs": False}
            body = tornado.escape.json_encode(id_dict)
            response = self.fetch(API_URL_PREFIX + "/store/download", method='POST', body=body)

            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            zf = zipfile.ZipFile(io.BytesIO(response.body), "r")
            info_list = zf.infolist()
            self.assertEqual(2, len(info_list))
            self.assertEqual("archive/dataset-0.txt", info_list[0].filename)
            self.assertEqual("archive/dataset-1.txt", info_list[1].filename)
        finally:
            if target_file_1 is not None:
                os.remove(target_file_1)
            if target_file_2 is not None:
                os.remove(target_file_2)
            if target_dir is not None:
                os.rmdir(target_dir)

    def test_post_one_invalid_ds_id(self):
        target_dir = None
        target_file_1 = None
        try:
            target_dir = os.path.join(self.ctx.store_path, "archive")
            os.makedirs(target_dir)

            ds_ref_1 = add_dataset(self.ctx, new_test_dataset(0))
            target_file_1 = os.path.join(self.ctx.store_path, ds_ref_1.path)
            with open(target_file_1, "w") as fp:
                fp.write("firlefanz")

            id_dict = {"id_list": [ds_ref_1.id, "does_not_exist"], "docs": False}
            body = tornado.escape.json_encode(id_dict)
            response = self.fetch(API_URL_PREFIX + "/store/download", method='POST', body=body)

            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            zf = zipfile.ZipFile(io.BytesIO(response.body), "r")
            info_list = zf.infolist()
            self.assertEqual(1, len(info_list))
            self.assertEqual("archive/dataset-0.txt", info_list[0].filename)
        finally:
            if target_file_1 is not None:
                os.remove(target_file_1)
            if target_dir is not None:
                os.rmdir(target_dir)


class StoreDownloadsubmissionFileTest(WsTestCase):
    def test_get(self):
        response = self.fetch(API_URL_PREFIX + f"/store/download/submissionfile/sd/0", method='GET')
        #self.assertEqual(400, response.code)
        #self.assertEqual('OK', response.reason)

        #expected_response_data = None
        #actual_response_data = response.body
        #self.assertEqual(expected_response_data, actual_response_data)



class DatasetsValidateTest(WsTestCase):

    def test_post(self):
        dataset = new_test_dataset(13)
        data = dataset.to_dict()
        body = tornado.escape.json_encode(data)
        response = self.fetch(API_URL_PREFIX + "/datasets/validate", method='POST', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertIsInstance(actual_response_data, dict)
        self.assertIn("status", actual_response_data)
        self.assertIn("OK", actual_response_data["status"])

        # @todo 1 tb/nf we need to discuss this wrt the validator now doing real validation 2019-02-05
        # dataset = new_test_dataset(13)
        # dataset.id = "gnartz!"
        # data = dataset.to_dict()
        # body = tornado.escape.json_encode(data)
        # response = self.fetch(API_URL_PREFIX + "/datasets/validate", method='POST', body=body)
        # self.assertEqual(200, response.code)
        # self.assertEqual('OK', response.reason)
        # actual_response_data = tornado.escape.json_decode(response.body)
        # self.assertIsInstance(actual_response_data, dict)
        # self.assertIn("status", actual_response_data)
        # self.assertIn("WARNING", actual_response_data["status"])


class DatasetsTest(WsTestCase):

    def test_get(self):
        add_dataset(self.ctx, new_test_dataset(0))
        add_dataset(self.ctx, new_test_dataset(1))
        add_dataset(self.ctx, new_test_dataset(2))
        add_dataset(self.ctx, new_test_dataset(3))

        expr = None
        region = None
        time = None
        wdepth = None
        mtype = "all"
        wlmode = "all"
        shallow = "no"
        pmode = 'contains'
        pgroup = None
        pname = None
        offset = None
        count = None

        args = dict(expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype, wlmode=wlmode, shallow=shallow,
                    pmode=pmode, pgroup=pgroup, pname=pname, offset=offset, count=count)
        query = urllib.parse.urlencode({k: v for k, v in args.items() if v is not None})

        response = self.fetch(API_URL_PREFIX + f"/datasets?{query}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertIn("total_count", actual_response_data)
        self.assertEqual(4, actual_response_data["total_count"])

    def test_get_multiple_pgroups(self):
        dataset = new_test_dataset(0)
        dataset.groups = ['chl_a']
        add_dataset(self.ctx, dataset)
        add_dataset(self.ctx, new_test_dataset(1))
        dataset = new_test_dataset(2)
        dataset.groups = ['a_pig']
        add_dataset(self.ctx, dataset)
        dataset = new_test_dataset(3)
        dataset.groups = ['b_part']
        add_dataset(self.ctx, dataset)

        query = 'mtype=all&wlmode=all&shallow=no&pmode=contains&pgroup=chl_a&pgroup=a_pig'

        response = self.fetch(API_URL_PREFIX + f"/datasets?{query}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertIn("total_count", actual_response_data)
        self.assertEqual(2, actual_response_data["total_count"])

    def test_get_multiple_pnames(self):
        dataset = new_test_dataset(0)
        dataset.attributes = ['cast']
        add_dataset(self.ctx, dataset)
        add_dataset(self.ctx, new_test_dataset(1))
        dataset = new_test_dataset(2)
        dataset.attributes = ['bottle']
        add_dataset(self.ctx, dataset)
        dataset = new_test_dataset(3)
        dataset.attributes = ['BACTABB']
        add_dataset(self.ctx, dataset)

        query = 'mtype=all&wlmode=all&shallow=no&pmode=contains&pname=BACTABB&pname=bottle'

        response = self.fetch(API_URL_PREFIX + f"/datasets?{query}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertIn("total_count", actual_response_data)
        self.assertEqual(2, actual_response_data["total_count"])

    def test_get_with_expression(self):
        dataset = new_test_dataset(0)
        dataset.metadata["experiment"] = "BOUSSOLE"
        add_dataset(self.ctx, dataset)
        add_dataset(self.ctx, new_test_dataset(1))
        dataset = new_test_dataset(2)
        dataset.metadata["experiment"] = "nizza"
        add_dataset(self.ctx, dataset)
        dataset = new_test_dataset(3)
        dataset.metadata["experiment"] = "BOUSSOLE"
        add_dataset(self.ctx, dataset)

        query = 'expr=experiment%3A%20%20*BOUSSOLE*'

        response = self.fetch(API_URL_PREFIX + f"/datasets?{query}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertIn("total_count", actual_response_data)
        self.assertEqual(2, actual_response_data["total_count"])

    def test_get_with_time_no_overlap(self):
        dataset = new_test_dataset(0)
        dataset.times = [datetime.datetime(1992, 4, 11, 16, 42, 19), datetime.datetime(1992, 4, 11, 18, 26, 37)]
        add_dataset(self.ctx, dataset)
        dataset = new_test_dataset(1)
        dataset.times = [datetime.datetime(1994, 9, 16, 19, 22, 8), datetime.datetime(1994, 9, 17, 2, 36, 18)]
        add_dataset(self.ctx, dataset)

        query = 'start_time=2010-01-01&end_time=2020-01-01'

        response = self.fetch(API_URL_PREFIX + f"/datasets?{query}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertIn("total_count", actual_response_data)
        self.assertEqual(0, actual_response_data["total_count"])

    def test_get_with_time_overlap(self):
        dataset = new_test_dataset(0)
        dataset.times = [datetime.datetime(1992, 4, 11, 16, 42, 19), datetime.datetime(1992, 4, 11, 18, 26, 37)]
        add_dataset(self.ctx, dataset)
        dataset = new_test_dataset(1)
        dataset.times = [datetime.datetime(1994, 9, 16, 19, 22, 8), datetime.datetime(1994, 9, 17, 2, 36, 18)]
        add_dataset(self.ctx, dataset)

        query = 'start_time=1992-01-01&end_time=1992-12-31'

        response = self.fetch(API_URL_PREFIX + f"/datasets?{query}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertIn("total_count", actual_response_data)
        self.assertEqual(1, actual_response_data["total_count"])

    def test_get_with_geojson(self):
        dataset = new_test_dataset(0)
        add_dataset(self.ctx, dataset)
        dataset = new_test_dataset(2)
        add_dataset(self.ctx, dataset)

        query = 'geojson=true'

        response = self.fetch(API_URL_PREFIX + f"/datasets?{query}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertIn("total_count", actual_response_data)
        self.assertEqual(2, actual_response_data["total_count"])

    def test_get_without_geojson(self):
        dataset = new_test_dataset(0)
        add_dataset(self.ctx, dataset)
        dataset = new_test_dataset(2)
        add_dataset(self.ctx, dataset)

        query = 'geojson=false'

        response = self.fetch(API_URL_PREFIX + f"/datasets?{query}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertIn("total_count", actual_response_data)
        self.assertEqual(2, actual_response_data["total_count"])

    def test_put(self):
        # test addDataset() operation
        dataset = new_test_dataset(13)
        body = tornado.escape.json_encode(dataset.to_dict())
        response = self.fetch(API_URL_PREFIX + "/datasets", method='PUT', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        query_result = find_datasets(self.ctx)
        self.assertEqual(1, query_result.total_count)
        self.assertEqual(dataset.path, query_result.datasets[0].path)

    def test_post(self):
        # updateDataset() operation
        add_dataset(self.ctx, new_test_dataset(14))
        query_result = find_datasets(self.ctx)
        self.assertEqual(1, query_result.total_count)
        dataset_id = query_result.datasets[0].id
        update_dataset = new_test_dataset(14)
        update_dataset.path = "a/b/c/archive/x/x-01.csv"
        update_dataset.id = dataset_id
        body = tornado.escape.json_encode(update_dataset.to_dict())
        response = self.fetch(API_URL_PREFIX + "/datasets", method='POST', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        updated_dataset = get_dataset_by_id_strict(self.ctx, dataset_id=dataset_id)
        self.assertEqual(update_dataset, updated_dataset)


class DatasetsIdTest(WsTestCase):
    @property
    def ctx(self):
        return self._app.ws_context

    def test_get(self):
        dataset_ref = add_dataset(self.ctx, new_test_dataset(0))
        dataset_id = dataset_ref.id
        response = self.fetch(API_URL_PREFIX + f"/datasets/{dataset_id}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertIn("id", actual_response_data)
        self.assertEqual(dataset_id, actual_response_data["id"])

        dataset_id = "gnarz-foop"
        response = self.fetch(API_URL_PREFIX + f"/datasets/{dataset_id}", method='GET')
        self.assertEqual(404, response.code)
        self.assertEqual('Dataset with ID gnarz-foop not found', response.reason)

    def test_delete(self):
        dataset_ref = add_dataset(self.ctx, new_test_dataset(0))
        dataset_id = dataset_ref.id
        response = self.fetch(API_URL_PREFIX + f"/datasets/{dataset_id}",
                              method='DELETE',
                              headers=dict(api_key="8745hfu57"))
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        response = self.fetch(API_URL_PREFIX + f"/datasets/{dataset_id}",
                              method='DELETE',
                              headers=dict(api_key="8745hfu57"))
        self.assertEqual(404, response.code)
        self.assertEqual(f'Dataset with ID {dataset_id} not found', response.reason)


class DatasetsAffilProjectCruiseTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_get(self):
        # TODO (generated): set path parameter(s) to reasonable value(s)
        affil = None
        project = None
        cruise = None

        response = self.fetch(API_URL_PREFIX + f"/datasets/{affil}/{project}/{cruise}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = []
        actual_response_data = []
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)


class DatasetsAffilProjectCruiseNameTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_get(self):
        # TODO (generated): set path parameter(s) to reasonable value(s)
        affil = None
        project = None
        cruise = None
        name = None

        response = self.fetch(API_URL_PREFIX + f"/datasets/{affil}/{project}/{cruise}/{name}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = None
        actual_response_data = response.body
        self.assertEqual(expected_response_data, actual_response_data)


class DatasetsIdQcinfoTest(WsTestCase):

    def test_get(self):
        dataset_ref = add_dataset(self.ctx, new_test_dataset(42))
        dataset_id = dataset_ref.id

        response = self.fetch(API_URL_PREFIX + f"/datasets/{dataset_id}/qcinfo", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        expected_response_data = {'date': None, 'result': None, 'status': 'SUBMITTED'}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)

    def test_post(self):
        dataset_ref = add_dataset(self.ctx, new_test_dataset(42))
        dataset_id = dataset_ref.id

        expected_qc_info = QcInfo(QC_STATUS_APPROVED,
                                  dict(by='Illaria',
                                       when="2019-02-01",
                                       doc_files=["qc-report.docx"]))
        body = tornado.escape.json_encode(expected_qc_info.to_dict())
        response = self.fetch(API_URL_PREFIX + f"/datasets/{dataset_id}/qcinfo", method='POST', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_qc_info = get_dataset_qc_info(self.ctx, dataset_id)
        self.assertEqual(expected_qc_info, actual_qc_info)


class DocfilesTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_put(self):
        # TODO (generated): set data for request body to reasonable value
        data = None
        body = data

        response = self.fetch(API_URL_PREFIX + "/docfiles", method='PUT', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)

    @unittest.skip('not implemented yet')
    def test_post(self):
        # TODO (generated): set data for request body to reasonable value
        data = None
        body = data

        response = self.fetch(API_URL_PREFIX + "/docfiles", method='POST', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)


class DocfilesAffilProjectCruiseTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_get(self):
        # TODO (generated): set path parameter(s) to reasonable value(s)
        affil = None
        project = None
        cruise = None

        response = self.fetch(API_URL_PREFIX + f"/docfiles/{affil}/{project}/{cruise}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = []
        actual_response_data = []
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)


class DocfilesAffilProjectCruiseNameTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_get(self):
        # TODO (generated): set path parameter(s) to reasonable value(s)
        affil = None
        project = None
        cruise = None
        name = None

        response = self.fetch(API_URL_PREFIX + f"/docfiles/{affil}/{project}/{cruise}/{name}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = None
        actual_response_data = response.body
        self.assertEqual(expected_response_data, actual_response_data)

    @unittest.skip('not implemented yet')
    def test_delete(self):
        # TODO (generated): set path parameter(s) to reasonable value(s)
        affil = None
        project = None
        cruise = None
        name = None

        response = self.fetch(API_URL_PREFIX + f"/docfiles/{affil}/{project}/{cruise}/{name}", method='DELETE')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)


class UsersTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_post(self):
        # TODO (generated): set data for request body to reasonable value
        data = {}
        body = tornado.escape.json_encode(data)

        response = self.fetch(API_URL_PREFIX + "/users", method='POST', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)


class UsersLoginTest(WsTestCase):

    def test_get(self):
        credentials = dict(username="scott", password="tiger")
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='POST', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        expected_response_data = {
            'id': 1,
            'name': 'scott',
            'email': 'bruce.scott@gmail.com',
            'first_name': 'Bruce',
            'last_name': 'Scott',
            'phone': '+34 5678901234',
            'roles': ['submit', 'admin']
        }
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)


class UsersLogoutTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_get(self):
        response = self.fetch(API_URL_PREFIX + "/users/logout", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)


class UsersIdTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_get(self):
        # TODO (generated): set path parameter(s) to reasonable value(s)
        id = None

        response = self.fetch(API_URL_PREFIX + f"/users/{id}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)

    @unittest.skip('not implemented yet')
    def test_put(self):
        # TODO (generated): set path parameter(s) to reasonable value(s)
        id = None

        # TODO (generated): set data for request body to reasonable value
        data = {}
        body = tornado.escape.json_encode(data)

        response = self.fetch(API_URL_PREFIX + f"/users/{id}", method='PUT', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)

    @unittest.skip('not implemented yet')
    def test_delete(self):
        # TODO (generated): set path parameter(s) to reasonable value(s)
        id = None

        response = self.fetch(API_URL_PREFIX + f"/users/{id}", method='DELETE')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)


class HelpersTest(unittest.TestCase):

    def test_ensure_string_argument_list(self):
        arg_value = ["heffalump"]

        string_value = _ensure_string_argument(arg_value, "name")
        self.assertTrue(isinstance(string_value, str))
        self.assertEqual("heffalump", string_value)

    def test_ensure_string_argument_list_wrong_size(self):
        arg_value = ["heffalump", "winnie"]

        try:
            _ensure_string_argument(arg_value, "name")
            self.fail("WsBadRequestError expected")
        except WsBadRequestError:
            pass

        try:
            _ensure_string_argument([], "name")
            self.fail("WsBadRequestError expected")
        except WsBadRequestError:
            pass

    def test_ensure_string_argument(self):
        string_value = _ensure_string_argument("nasenmann", "name")
        self.assertTrue(isinstance(string_value, str))
        self.assertEqual("nasenmann", string_value)

    def test_ensure_string_argument_wrong_type(self):
        try:
            _ensure_string_argument(118876, "name")
            self.fail("WsBadRequestError expected")
        except WsBadRequestError:
            pass

    def test_ensure_string_argument_decodes_byte_array(self):
        string_as_bytes = "hampelmann".encode()

        str_val = _ensure_string_argument(string_as_bytes, "name")
        self.assertEqual("hampelmann", str_val)

    def test_ensure_integer_argument_list(self):
        arg_value = [95523]

        int_value = _ensure_int_argument(arg_value, "name")
        self.assertTrue(isinstance(int_value, int))
        self.assertEqual(95523, int_value)

    def test_ensure_integer_argument_list_wrong_size(self):
        arg_value = [99, 100]

        try:
            _ensure_int_argument(arg_value, "name")
            self.fail("WsBadRequestError expected")
        except WsBadRequestError:
            pass

        try:
            _ensure_int_argument([], "name")
            self.fail("WsBadRequestError expected")
        except WsBadRequestError:
            pass

    def test_ensure_integer_argument(self):
        int_value = _ensure_int_argument(101, "name")
        self.assertTrue(isinstance(int_value, int))
        self.assertEqual(101, int_value)

    def test_ensure_int_argument_wrong_type(self):
        try:
            _ensure_int_argument("hoppla!", "name")
            self.fail("WsBadRequestError expected")
        except WsBadRequestError:
            pass
