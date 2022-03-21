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
import tempfile
import unittest
import urllib.parse
import zipfile
from typing import Optional

import tornado.escape
import tornado.testing

from ocdb.core.db.db_submission import DbSubmission
from ocdb.core.db.db_user import DbUser
from ocdb.core.models import DatasetValidationResult, Issue, User
from ocdb.core.models.qc_info import QcInfo, QC_STATUS_SUBMITTED, \
    QC_STATUS_VALIDATED, QC_STATUS_APPROVED
from ocdb.core.models.submission import Submission, TYPE_MEASUREMENT
from ocdb.core.models.submission_file import SubmissionFile
from ocdb.core.roles import Roles
from ocdb.version import MIN_CLIENT_VERSION
from ocdb.ws.app import new_application
from ocdb.ws.controllers.datasets import add_dataset, get_dataset_qc_info
from ocdb.ws.controllers.users import create_user
from ocdb.ws.handlers import API_URL_PREFIX
# noinspection PyProtectedMember
from ocdb.ws.handlers._handlers import _ensure_string_argument, WsBadRequestError, _ensure_int_argument, \
    UpdateSubmissionStatus
from tests.core.mpf import MultiPartForm
from tests.helpers import new_test_service_context, new_test_dataset, NOW


TEST_DATA = """/begin_header
/identifier_product_doi=10.5067/SeaBASS/SCOTIA_PRINCE_FERRY/DATA001
/received=20040220
/affiliations=Bigelow_Laboratory_for_Ocean_Sciences
/investigators=William_Balch
/contact=bbalch@bigelow.org
/experiment=Scotia_Prince_ferry
/cruise=s030603w
/data_type=cast
/west_longitude=-66.4551[DEG]
/east_longitude=-66.4551[DEG]
/north_latitude=43.7621[DEG]
/south_latitude=43.7621[DEG]
/start_date=20030603
/end_date=20030603
/start_time=14:00:38[GMT]
/end_time=14:00:38[GMT]
/fields=date,time,lat,lon,depth,wt
/units=yyyymmdd,hh:mm:ss,degrees,degrees,meters,degreesc
/data_status=final
/delimiter=space
/documents=readme.txt
/data_file_name=T0_00686.EDF
/missing=-99.99
/water_depth=NA
/wind_speed=NA
/wave_height=NA
/secchi_depth=NA
/cloud_percent=NA
/station=NA
/calibration_files=no-calibration-file.txt
/end_header
20030603 14:00:38 43.7620 -66.4551 0.60 8.37
20030603 14:00:38 43.7620 -66.4551 1.30 7.05
"""


TEST_DATA_FILE_NAME = ""


class WsTestCase(tornado.testing.AsyncHTTPTestCase):
    def setUp(self):
        super(WsTestCase, self).setUp()
        user = DbUser(
            id_='asdoökvn',
            name="submit",
            password="submit",
            first_name='Submit',
            last_name="Submit",
            email="",
            phone="",
            roles=["submit", ]
        )
        create_user(ctx=self.ctx, user=user)

        user = DbUser(
            id_='eocdb_chef_id',
            name="chef",
            password="eocdb_chef",
            first_name='eocdb',
            last_name="chef",
            email="",
            phone="",
            roles=["submit", "admin"]
        )
        create_user(ctx=self.ctx, user=user)

        submission_id = "I_DO_EXIST"
        files = [SubmissionFile(submission_id=submission_id,
                                index=0,
                                creationdate=NOW,
                                filename="Hans",
                                filetype="black",
                                status=QC_STATUS_SUBMITTED,
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id=submission_id,
                                index=1,
                                creationdate=NOW,
                                filename="Helga",
                                filetype="green",
                                status=QC_STATUS_VALIDATED,
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]

        submission = DbSubmission(submission_id=submission_id,
                                  user_id='chef',
                                  date=datetime.datetime.now(),
                                  status="who_knows",
                                  qc_status="OK",
                                  path="temp",
                                  publication_date='2001-02-03T04:05:06',
                                  allow_publication=False,
                                  files=files,
                                  store_user_path='Tom_Helge')
        self.ctx.db_driver.add_submission(submission)

        submission_id = "I_DO_EXIST_MINE"
        files = [SubmissionFile(submission_id=submission_id,
                                index=0,
                                creationdate=NOW,
                                filename="Hans",
                                filetype="black",
                                status=QC_STATUS_SUBMITTED,
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id=submission_id,
                                index=1,
                                creationdate=NOW,
                                filename="Helga",
                                filetype="green",
                                status=QC_STATUS_VALIDATED,
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]
        submission = DbSubmission(submission_id=submission_id,
                                  user_id='submit',
                                  date=datetime.datetime.now(),
                                  status="who_knows",
                                  qc_status="OK",
                                  path="temp",
                                  publication_date='2001-02-03T04:05:06',
                                  allow_publication=False,
                                  files=files,
                                  store_user_path='Tom_Helge')
        self.ctx.db_driver.add_submission(submission)

        fp = tempfile.NamedTemporaryFile(delete=False, suffix='.sb', mode='w')
        fp.write(TEST_DATA)
        global TEST_DATA_FILE_NAME
        TEST_DATA_FILE_NAME = fp.name
        fp.close()

    def get_app(self):
        """Implements AsyncHTTPTestCase.get_app()."""
        application = new_application()
        application.ws_context = new_test_service_context()
        return application

    @property
    def ctx(self):
        return self._app.ws_context

    def login_admin(self, client_version=None) -> Optional[str]:
        client_version = client_version or MIN_CLIENT_VERSION
        credentials = {'username': "chef", 'password': "eocdb_chef", 'client_version': client_version}
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='POST', body=body)
        self.assertEqual(200, response.code)

        return response.headers._dict["Set-Cookie"]

    def logout_admin(self):
        response = self.fetch(API_URL_PREFIX + "/users/logout", method='GET')
        self.assertEqual(200, response.code)

    def login_admin_no_assert(self, client_version=None):
        client_version = client_version or MIN_CLIENT_VERSION
        credentials = {'username': "chef", 'password': "eocdb_chef", 'client_version': client_version}
        body = tornado.escape.json_encode(credentials)

        return self.fetch(API_URL_PREFIX + f"/users/login", method='POST', body=body)

    def login_submit(self) -> Optional[str]:
        credentials = {'username': "submit", 'password': "submit", 'client_version': MIN_CLIENT_VERSION}
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='POST', body=body)

        return response.headers._dict["Set-Cookie"]

    def logout_submit(self):
        response = self.fetch(API_URL_PREFIX + "/users/logout", method='GET')
        self.assertEqual(200, response.code)


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
        self.assertEqual("ocdb-server", result["info"].get("title"))
        self.assertEqual("0.1.19", result["info"].get("version"))
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


class HandleSubmissionTest(WsTestCase):

    def test_post_invalid_submission_id(self):
        cookie = self.login_admin()
        try:
            mpf = MultiPartForm(boundary="HEFFALUMP")
            mpf.add_field("submissionid", "")

            response = self.fetch(API_URL_PREFIX + "/store/upload/submission", method='POST', body=bytes(mpf),
                                  headers={"Cookie": cookie})
            self.assertEqual(400, response.code)
            self.assertEqual("Invalid argument 'submissionid' in body: None", response.reason)
        finally:
            self.logout_admin()

    def test_post_invalid_path(self):
        cookie = self.login_admin()
        try:
            mpf = MultiPartForm(boundary="HEFFALUMP")
            mpf.add_field("path", "/home/helge/ohje")

            response = self.fetch(API_URL_PREFIX + "/store/upload/submission", method='POST', body=bytes(mpf),
                                  headers={"Cookie": cookie})

            self.assertEqual(400, response.code)
            self.assertEqual("Invalid argument 'submissionid' in body: None", response.reason)
        finally:
            self.logout_admin()

    def test_post_submission_id_already_present(self):
        cookie = self.login_admin()
        try:
            submission_id = "I_DO_EXIST"
            submission = Submission(submission_id=submission_id,
                                    user_id='12',
                                    date=datetime.datetime.now(),
                                    status="who_knows",
                                    qc_status="OK",
                                    publication_date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                    allow_publication=False,
                                    file_refs=[])
            self.ctx.db_driver.add_submission(submission)

            mpf = MultiPartForm(boundary="HEFFALUMP")
            mpf.add_field("submissionid", submission_id)

            response = self.fetch(API_URL_PREFIX + "/store/upload/submission", method='POST', body=bytes(mpf),
                                  headers={"Cookie": cookie})
            self.assertEqual(400, response.code)
            self.assertEqual("Invalid argument 'submissionid' in body: None", response.reason)
        finally:
            self.logout_admin()

    def test_post_submission(self):
        cookie = self.login_admin()
        try:

            form = MultiPartForm()
            form.add_field('path', "KK/KK/KK")
            form.add_field('submissionid', "PUB_NOT_ALLOWED")

            form.add_field('publicationdate', str(datetime.datetime(2001, 2, 3, 4, 5, 6)))
            form.add_field('allowpublication', str(True))

            form.add_file(f'datasetfiles', os.path.basename(TEST_DATA_FILE_NAME), TEST_DATA_FILE_NAME,
                          mime_type="text/plain")

            data = bytes(form)

            response = self.fetch(API_URL_PREFIX + "/store/upload/submission", method='POST', body=data,
                                  headers={"Cookie": cookie, 'Content-length': len(data),
                                           'Content-type': form.content_type})

            self.assertEqual(200, response.code)

            response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/PUB_NOT_ALLOWED", method='GET',
                                  headers={"Cookie": cookie})

            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            actual_response_data = tornado.escape.json_decode(response.body)
            del actual_response_data["id"]  # varies, therefore we do not check
            del actual_response_data["date"]  # varies, therefore we do not check
            del actual_response_data["files"][0]['creationdate']  # varies, therefore we do not check

            expected_response_data = {'submission_id': 'PUB_NOT_ALLOWED',
                                      'user_id': 'chef',
                                      'status': 'VALIDATED',
                                      'publication_date': '2001-02-03 04:05:06',
                                      'qc_status': 'OK',
                                      'file_refs': [],
                                      'allow_publication': True,
                                      'path': 'KK/KK/KK',
                                      'store_sub_path': 'chef_PUB_NOT_ALLOWED',
                                      'files': [
                                          {'index': 0,
                                           'submission_id': 'PUB_NOT_ALLOWED',
                                           'filename': os.path.basename(TEST_DATA_FILE_NAME),
                                           'filetype': 'MEASUREMENT',
                                           'status': 'OK',
                                           'result': {'status': 'OK', 'issues': []}
                                           }
                                      ]
                                      }
            self.assertEqual(expected_response_data, actual_response_data)

        finally:
            self.logout_admin()

    def test_post_submission_pub_not_allowed(self):
        cookie = self.login_admin()
        try:

            form = MultiPartForm()
            form.add_field('path', "KK/KK/KK")
            form.add_field('submissionid', "PUB_NOT_ALLOWED")

            form.add_field('publicationdate', str(None))
            form.add_field('allowpublication', str(False))

            form.add_file(f'datasetfiles', os.path.basename(TEST_DATA_FILE_NAME), TEST_DATA_FILE_NAME,
                          mime_type="text/plain")

            data = bytes(form)

            response = self.fetch(API_URL_PREFIX + "/store/upload/submission", method='POST', body=data,
                                  headers={"Cookie": cookie, 'Content-length': len(data),
                                           'Content-type': form.content_type})

            self.assertEqual(200, response.code)

            response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/PUB_NOT_ALLOWED", method='GET',
                                  headers={"Cookie": cookie})

            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            actual_response_data = tornado.escape.json_decode(response.body)
            self.assertEqual(False, actual_response_data['allow_publication'])
            self.assertEqual(None, actual_response_data['publication_date'])

        finally:
            self.logout_admin()

    def test_post_not_logged_in(self):
        mpf = MultiPartForm(boundary="HEFFALUMP")
        mpf.add_field("submissionid", "whatever")

        response = self.fetch(API_URL_PREFIX + "/store/upload/submission", method='POST', body=bytes(mpf))
        self.assertEqual(403, response.code)
        self.assertEqual("Please login.", response.reason)

    def test_delete_invalid_id(self):
        cookie = self.login_admin()
        try:
            response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/ABCDEFGHI", method='DELETE',
                                  headers={"Cookie": cookie})

            self.assertEqual(404, response.code)
            self.assertEqual('Submission not found', response.reason)
        finally:
            self.logout_admin()

    def test_delete_success(self):
        cookie = self.login_admin()
        try:
            submission_id = "I_DO_EXIST"
            submission = DbSubmission(submission_id=submission_id,
                                      user_id='12',
                                      date=datetime.datetime.now(),
                                      status="who_knows",
                                      qc_status="OK",
                                      path="temp",
                                      publication_date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                      allow_publication=False,
                                      files=[],
                                      store_user_path='Tom_Helge')
            self.ctx.db_driver.add_submission(submission)

            response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/I_DO_EXIST", method='DELETE',
                                  headers={"Cookie": cookie})

            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)
        finally:
            self.logout_admin()

    def test_delete_not_logged_in(self):
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/dontcare", method='DELETE')

        self.assertEqual(403, response.code)
        self.assertEqual("Please login.", response.reason)

    def test_delete_not_belong(self):
        cookie = self.login_submit()

        response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/I_DO_EXIST", method='DELETE',
                              headers={"Cookie": cookie})

        self.assertEqual(403, response.code)
        self.assertEqual("Not enough access rights to perform operations on submission I_DO_EXIST.", response.reason)

    def test_get_invalid_id(self):
        cookie = self.login_admin()
        try:
            response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/ABCDEFGHI", method='GET',
                                  headers={"Cookie": cookie})

            self.assertEqual(404, response.code)
            self.assertEqual('Submission not found', response.reason)
        finally:
            self.logout_admin()

    def test_get_success(self):
        cookie = self.login_admin()
        try:
            submission_id = "I_DO_EXIST2"
            submission = DbSubmission(submission_id=submission_id,
                                      user_id='12',
                                      date=datetime.datetime.now(),
                                      status="who_knows",
                                      qc_status="OK",
                                      path="temp",
                                      publication_date='2001-02-03T04:05:06',
                                      allow_publication=False,
                                      files=[],
                                      store_user_path='Tom_Helge')
            self.ctx.db_driver.add_submission(submission)

            response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/I_DO_EXIST2", method='GET',
                                  headers={"Cookie": cookie})

            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            actual_response_data = tornado.escape.json_decode(response.body)
            del actual_response_data["date"]  # varies, therefore we do not check tb 2019-03-13
            del actual_response_data["id"]  # varies, therefore we do not check tb 2019-03-13
            self.assertEqual({
                'file_refs': [],
                'files': [],
                'path': 'temp',
                'publication_date': '2001-02-03T04:05:06',
                'allow_publication': False,
                'qc_status': 'OK',
                'status': 'who_knows',
                'store_sub_path': 'Tom_Helge',
                'submission_id': 'I_DO_EXIST2',
                'user_id': '12'}, actual_response_data)
        finally:
            self.logout_admin()

    def test_get_not_logged_in(self):
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/ABCDEFGHI", method='GET')

        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test_get_not_belong(self):
        cookie = self.login_submit()
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/I_DO_EXIST", method='GET',
                              headers={"Cookie": cookie})

        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operations on submission I_DO_EXIST.', response.reason)


class UpdateSubmissionStatusTest(WsTestCase):

    def test_put_invalid_id(self):
        cookie = self.login_admin()
        try:
            body = tornado.escape.json_encode({"status": QC_STATUS_APPROVED, "date": "20170822"})
            response = self.fetch(API_URL_PREFIX + f"/store/status/submission/abcdefghijick", body=body, method='PUT',
                                  headers={"Cookie": cookie})

            self.assertEqual(404, response.code)
            self.assertEqual('Submission not found', response.reason)
        finally:
            self.logout_admin()

    def test_put_approve(self):
        cookie = self.login_admin()
        try:
            submission_id = "I_DO_EXIST2"
            submission = DbSubmission(submission_id=submission_id,
                                      user_id='12',
                                      date=datetime.datetime.now(),
                                      status=QC_STATUS_VALIDATED,
                                      qc_status="OK",
                                      path="temp",
                                      publication_date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                      allow_publication=False,
                                      files=[],
                                      store_user_path='Tom_Helge')
            self.ctx.db_driver.add_submission(submission)

            body = tornado.escape.json_encode({"status": QC_STATUS_APPROVED,
                                               "date": "20180923",
                                               'publication_date': '20180923',
                                               'allow_publication': False,
                                               })
            response = self.fetch(API_URL_PREFIX + f"/store/status/submission/{submission_id}", body=body, method='PUT',
                                  headers={"Cookie": cookie})
            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/{submission_id}", method='GET',
                                  headers={"Cookie": cookie})
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
                'store_sub_path': 'Tom_Helge',
                'submission_id': 'I_DO_EXIST2',
                'publication_date': None,  # !!! Comes in here as None. Should ba a date.!! Need to check
                'allow_publication': False,
                'user_id': '12'}, actual_response_data)
        finally:
            self.logout_admin()

    def test_put_not_logged_in(self):
        body = tornado.escape.json_encode({"status": QC_STATUS_APPROVED, "date": "20170822"})
        response = self.fetch(API_URL_PREFIX + f"/store/status/submission/I_DO_EXIST", body=body, method='PUT')

        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test_put_not_belong(self):
        body = tornado.escape.json_encode({"status": QC_STATUS_APPROVED, "date": "20170822"})
        response = self.fetch(API_URL_PREFIX + f"/store/status/submission/I_DO_EXIST", body=body, method='PUT',
                              headers={"Cookie": self.login_submit()})

        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operations on submission I_DO_EXIST.', response.reason)

    def test_extract_date_not_present(self):
        body_dict = {"status": "whatever"}

        date = UpdateSubmissionStatus._extract_date(body_dict)
        self.assertIsNone(date)

    def test_extract_date(self):
        body_dict = {"status": "whatever", "date": "20180317"}

        date = UpdateSubmissionStatus._extract_date(body_dict)
        self.assertIsNotNone(date)
        self.assertEqual(2018, date.tm_year)
        self.assertEqual(3, date.tm_mon)
        self.assertEqual(17, date.tm_mday)


class HandleSubmissionFileTest(WsTestCase):

    def test_get_no_results(self):
        cookie = self.login_admin()
        try:
            response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/ABCDEFGHI/0", method='GET',
                                  headers={"Cookie": cookie})

            self.assertEqual(400, response.code)
            self.assertEqual('No result found', response.reason)
        finally:
            self.logout_admin()

    def test_get_one_result(self):
        cookie = self.login_admin()
        try:
            user = User(name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                        first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

            mid = create_user(self.ctx, user)

            # --- add submission file ---
            files = [SubmissionFile(submission_id="submitme",
                                    index=0,
                                    creationdate=NOW,
                                    filename="Hans",
                                    filetype="black",
                                    status=QC_STATUS_SUBMITTED,
                                    result=DatasetValidationResult(status="OK", issues=[])),
                     SubmissionFile(submission_id="submitme",
                                    index=1,
                                    creationdate=NOW,
                                    filename="Helga",
                                    filetype="green",
                                    status=QC_STATUS_VALIDATED,
                                    result=DatasetValidationResult(status="WARNING", issues=[
                                        Issue(type="WARNING", description="This might be wrong")]))]
            db_subm = DbSubmission(status="Hellyeah", user_id=mid, submission_id="submitme", files=files,
                                   qc_status="OK",
                                   path="/root/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                   publication_date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                   allow_publication=False,
                                   store_user_path='Tom_Helge')
            self.ctx.db_driver.add_submission(db_subm)

            # --- get submission file ---
            response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/submitme/0", method='GET',
                                  headers={"Cookie": cookie})

            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            actual_response_data = tornado.escape.json_decode(response.body)
            self.assertEqual({'filename': 'Hans',
                              'creationdate': '2009-08-07T06:05:04',
                              'filetype': 'black',
                              'index': 0,
                              'result': {'issues': [], 'status': 'OK'},
                              'status': 'SUBMITTED',
                              'submission_id': 'submitme'}, actual_response_data)
        finally:
            self.logout_admin()

    def test_get_not_loged_in(self):
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/ABCDEFGHI/0", method='GET')

        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test_get_not_belong(self):
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/I_DO_EXIST/0", method='GET',
                              headers={"Cookie": self.login_submit()})

        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operations on submission I_DO_EXIST.', response.reason)

    def test_delete_no_submissions(self):
        cookie = self.login_admin()
        try:
            response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/ABCDEFGHI/0", method='DELETE',
                                  headers={"Cookie": cookie})

            self.assertEqual(404, response.code)
            self.assertEqual('Submission not found', response.reason)
        finally:
            self.logout_admin()

    def test_delete(self):
        cookie = self.login_admin()
        try:
            user = self.ctx.get_user("chef")
            files = [SubmissionFile(submission_id="submitme",
                                    index=0,
                                    filename="Hans",
                                    creationdate=NOW,
                                    filetype="black",
                                    status=QC_STATUS_SUBMITTED,
                                    result=DatasetValidationResult(status="OK", issues=[])),
                     SubmissionFile(submission_id="submitme",
                                    index=1,
                                    creationdate=NOW,
                                    filename="Helga",
                                    filetype="green",
                                    status=QC_STATUS_VALIDATED,
                                    result=DatasetValidationResult(status="WARNING", issues=[
                                        Issue(type="WARNING", description="This might be wrong")]))]
            db_subm = DbSubmission(status="Hellyeah", user_id=user.id, submission_id="submitme", files=files,
                                   qc_status="OK",
                                   path="/root/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                   publication_date='2001-02-03T04:05:06',
                                   allow_publication=False,
                                   store_user_path='Tom_Helge')
            self.ctx.db_driver.add_submission(db_subm)

            response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/submitme/0", method='DELETE',
                                  headers={"Cookie": cookie})
            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            response = self.fetch(API_URL_PREFIX + f"/store/upload/submission/submitme", method='GET',
                                  headers={"Cookie": cookie})
            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)
            actual_response_data = tornado.escape.json_decode(response.body)
            self.assertEqual(1, len(actual_response_data['files']))
        finally:
            self.logout_admin()

    def test_delete_not_logged_in(self):
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/ABCDEFGHI/0", method='DELETE')

        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test_delete_not_belong(self):
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/I_DO_EXIST/0", method='DELETE',
                              headers={"Cookie": self.login_submit()})

        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operations on submission I_DO_EXIST.', response.reason)

    def test_put_invalid_submissionid(self):
        cookie = self.login_admin()
        try:
            submissionid = "rattelschneck"
            mpf = MultiPartForm(boundary="HEFFALUMP")
            mpf.add_field("submissionid", submissionid)
            index = 0
            response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/{submissionid}/{index}", method='PUT',
                                  body=bytes(mpf), headers={"Cookie": cookie})

            self.assertEqual(404, response.code)
            self.assertEqual('Submission not found', response.reason)
        finally:
            self.logout_admin()

    def test_put_no_body(self):
        cookie = self.login_admin()
        try:
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
            db_subm = DbSubmission(status="Hellyeah", user_id='88763', submission_id=submissionid, files=files,
                                   qc_status="OK",
                                   path="/root/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                   store_user_path='Tom_Helge')
            self.ctx.db_driver.add_submission(db_subm)

            mpf = MultiPartForm(boundary="HEFFALUMP")
            mpf.add_field("submissionid", submissionid)
            index = 0
            response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/{submissionid}/{index}", method='PUT',
                                  body=bytes(mpf), headers={"Content-Type": mpf.content_type, "Cookie": cookie})

            self.assertEqual(400, response.code)
            self.assertEqual('Invalid number of files supplied', response.reason)
        finally:
            self.logout_admin()

    def test_put_invalid_index(self):
        cookie = self.login_admin()
        try:
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
            db_subm = DbSubmission(status="Hellyeah", user_id='88763', submission_id=submissionid, files=files,
                                   qc_status="OK",
                                   path="/root/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                   store_user_path='Tom_Helge')
            self.ctx.db_driver.add_submission(db_subm)

            index = -2
            mpf = MultiPartForm(boundary="HEFFALUMP")
            mpf.add_field("submissionid", submissionid)
            dataset = self._create_valid_dataset()
            mpf.add_file(f'datasetfiles', "the_uploaded_file.sb", io.StringIO(dataset), mime_type="text/plain")
            response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/{submissionid}/{index}", method='PUT',
                                  body=bytes(mpf), headers={"Content-Type": mpf.content_type, "Cookie": cookie})

            self.assertEqual(400, response.code)
            self.assertEqual('Invalid submission file index', response.reason)
        finally:
            self.logout_admin()

    def test_put_success(self):
        cookie = self.login_admin()
        try:
            submissionid = "rabatz"
            files = [SubmissionFile(submission_id=submissionid,
                                    index=0,
                                    creationdate=NOW,
                                    filename="Hans",
                                    filetype="black",
                                    status=QC_STATUS_SUBMITTED,
                                    result=DatasetValidationResult(status="OK", issues=[])),
                     SubmissionFile(submission_id=submissionid,
                                    index=1,
                                    creationdate=NOW,
                                    filename="Helga",
                                    filetype="MEASUREMENT",
                                    status=QC_STATUS_VALIDATED,
                                    result=DatasetValidationResult(status="WARNING", issues=[
                                        Issue(type="WARNING", description="This might be wrong")]))]
            db_subm = DbSubmission(status="Hellyeah", user_id='88763', submission_id=submissionid, files=files,
                                   qc_status=QC_STATUS_VALIDATED,
                                   path="/tmp/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                   store_user_path='Tom_Helge')
            self.ctx.db_driver.add_submission(db_subm)

            index = 1
            mpf = MultiPartForm(boundary="HEFFALUMP")
            mpf.add_field("submissionid", submissionid)
            dataset = self._create_valid_dataset()
            mpf.add_file(f'files', "the_uploaded_file.sb", io.StringIO(dataset), mime_type="text/plain")
            response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/{submissionid}/{index}", method='PUT',
                                  body=bytes(mpf), headers={"Content-Type": mpf.content_type, "Cookie": cookie})

            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/{submissionid}/{index}", method='GET',
                                  headers={"Cookie": cookie})

            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            actual_response_data = tornado.escape.json_decode(response.body)
            self.assertEqual({'filename': 'the_uploaded_file.sb',
                              'filetype': TYPE_MEASUREMENT,
                              'index': 1,
                              'creationdate': '2009-08-07T06:05:04',
                              'result': {'issues': [], 'status': 'OK'},
                              'status': "OK",
                              'submission_id': 'rabatz'}, actual_response_data)
        finally:
            self.logout_admin()

    def test_put_not_logged_in(self):
        submissionid = "rattelschneck"
        mpf = MultiPartForm(boundary="HEFFALUMP")
        mpf.add_field("submissionid", submissionid)
        index = 0
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/{submissionid}/{index}", method='PUT',
                              body=bytes(mpf))

        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test_put_not_belong(self):
        submissionid = "I_DO_EXIST"
        mpf = MultiPartForm(boundary="HEFFALUMP")
        mpf.add_field("submissionid", submissionid)
        index = 0
        response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/{submissionid}/{index}", method='PUT',
                              body=bytes(mpf),
                              headers={"Content-Type": mpf.content_type, "Cookie": self.login_submit()})

        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operations on submission I_DO_EXIST.', response.reason)

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


class UpdateSubmissionFileStatusTest(WsTestCase):

    def test_update_invalid_submissionfile(self):
        cookie = self.login_admin()
        try:
            submission_id = "not_stored"
            index = 8
            status = QC_STATUS_VALIDATED

            response = self.fetch(API_URL_PREFIX + f"/store/status/submissionfile/{submission_id}/{index}/{status}",
                                  method='GET', headers={"Cookie": cookie})

            self.assertEqual(404, response.code)
            self.assertEqual('Submission not found', response.reason)
        finally:
            self.logout_admin()

    def test_update_invalid_index(self):
        cookie = self.login_admin()
        try:
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
            db_subm = DbSubmission(status="Hellyeah", user_id='88763', submission_id="submitme", files=files,
                                   qc_status="OK",
                                   path="/root/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                   store_user_path='Tom_Helge')
            self.ctx.db_driver.add_submission(db_subm)

            submission_id = "submitme"
            index = 8
            status = QC_STATUS_APPROVED
            response = self.fetch(API_URL_PREFIX + f"/store/status/submissionfile/{submission_id}/{index}/{status}",
                                  method='GET',
                                  headers={"Cookie": cookie})

            self.assertEqual(400, response.code)
            self.assertEqual('Invalid submission file index', response.reason)
        finally:
            self.logout_admin()

    def test_update_success(self):
        cookie = self.login_admin()
        try:
            files = [SubmissionFile(submission_id="submitme",
                                    creationdate=NOW,
                                    index=0,
                                    filename="Hans",
                                    filetype="black",
                                    status=QC_STATUS_SUBMITTED,
                                    result=DatasetValidationResult(status="OK", issues=[])),
                     SubmissionFile(submission_id="submitme",
                                    creationdate=NOW,
                                    index=1,
                                    filename="Helga",
                                    filetype="green",
                                    status=QC_STATUS_VALIDATED,
                                    result=DatasetValidationResult(status="WARNING", issues=[
                                        Issue(type="WARNING", description="This might be wrong")]))]
            db_subm = DbSubmission(status="Hellyeah", user_id='88763', submission_id="submitme", files=files,
                                   qc_status="OK",
                                   path="/root/hell/yeah", date=datetime.datetime(2001, 2, 3, 4, 5, 6),
                                   store_user_path='Tom_Helge')
            self.ctx.db_driver.add_submission(db_subm)

            submission_id = "submitme"
            index = 1
            status = QC_STATUS_APPROVED
            response = self.fetch(API_URL_PREFIX + f"/store/status/submissionfile/{submission_id}/{index}/{status}",
                                  method='GET',
                                  headers={"Cookie": cookie})

            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            response = self.fetch(API_URL_PREFIX + f"/store/upload/submissionfile/submitme/1", method='GET',
                                  headers={"Cookie": cookie})

            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            actual_response_data = tornado.escape.json_decode(response.body)
            self.assertEqual({'filename': 'Helga',
                              'creationdate': '2009-08-07T06:05:04',
                              'filetype': 'green',
                              'index': 1,
                              'result': {'issues': [{'description': 'This might be wrong',
                                                     'type': 'WARNING'}],
                                         'status': 'WARNING'},
                              'status': 'APPROVED',
                              'submission_id': 'submitme'}, actual_response_data)
        finally:
            self.logout_admin()

    def test_update_not_logged_in(self):
        submission_id = "not_stored"
        index = 8
        status = QC_STATUS_VALIDATED

        response = self.fetch(API_URL_PREFIX + f"/store/status/submissionfile/{submission_id}/{index}/{status}",
                              method='GET')

        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test_update_not_belong(self):
        submission_id = "I_DO_EXIST"
        index = 8
        status = QC_STATUS_VALIDATED

        response = self.fetch(API_URL_PREFIX + f"/store/status/submissionfile/{submission_id}/{index}/{status}",
                              method='GET', headers={"Cookie": self.login_submit()})

        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operations on submission I_DO_EXIST.', response.reason)


class GetSubmissionsForUserTest(WsTestCase):
    def test_get_not_logged_in1(self):
        response = self.fetch(API_URL_PREFIX + f"/store/upload/user", method='GET')

        self.assertEqual(404, response.code)

    def test_get_not_logged_in2(self):
        response = self.fetch(API_URL_PREFIX + f"/store/upload/user/helge", method='GET')

        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test_get_as_admin(self):
        cookie = self.login_admin()

        response = self.fetch(API_URL_PREFIX + f"/store/upload/user/chef", method='GET', headers={"Cookie": cookie})
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self.assertEqual(2, len(actual_response_data))
        self.logout_admin()

    def test_get_as_submit(self):
        cookie = self.login_submit()

        response = self.fetch(API_URL_PREFIX + f"/store/upload/user/submit", method='GET', headers={"Cookie": cookie})
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self.assertEqual(2, len(actual_response_data))
        self.logout_submit()

    def test_get_query_user_as_submit(self):
        cookie = self.login_submit()

        response = self.fetch(API_URL_PREFIX + f"/store/upload/user/submit?"
                                               f"query-column=user_id&query-operator=equals&query-value=submit2",
                              method='GET', headers={"Cookie": cookie})
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self.assertEqual(2, len(actual_response_data))
        self.assertEqual('submit', actual_response_data['submissions'][0]['user_id'])
        self.logout_submit()

    def test_get_submit_attempt_query_other_user(self):
        cookie = self.login_submit()

        response = self.fetch(API_URL_PREFIX + f"/store/upload/user/submit2?"
                                               f"query-column=user_id&query-operator=equals&query-value=submit2",
                              method='GET', headers={"Cookie": cookie})
        self.assertEqual(401, response.code)
        self.logout_submit()


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
            target_dir = os.path.join(self.ctx.store_path, '1_abc',
                                      "archive", "archive")
            os.makedirs(target_dir, exist_ok=True)

            ds_ref_1 = add_dataset(self.ctx, new_test_dataset(0))
            target_file_1 = os.path.join(self.ctx.store_path, '1_abc',
                                         ds_ref_1.path, "archive", ds_ref_1.filename)
            with open(target_file_1, "w") as fp:
                fp.write("firlefanz")

            ds_ref_2 = add_dataset(self.ctx, new_test_dataset(1))
            target_file_2 = os.path.join(self.ctx.store_path, '1_abc',
                                         ds_ref_2.path, "archive", ds_ref_2.filename)
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
            self.assertEqual("archive/archive/dataset-0.txt", info_list[0].filename)
            self.assertEqual("archive/archive/dataset-1.txt", info_list[1].filename)
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
            target_dir = os.path.join(self.ctx.store_path, '1_abc',
                                      "archive", "archive")
            os.makedirs(target_dir)

            ds_ref_1 = add_dataset(self.ctx, new_test_dataset(0))
            target_file_1 = os.path.join(self.ctx.store_path, '1_abc',
                                         ds_ref_1.path, "archive", ds_ref_1.filename)
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
            self.assertEqual("archive/archive/dataset-0.txt", info_list[0].filename)
        finally:
            if target_file_1 is not None:
                os.remove(target_file_1)
            if target_dir is not None:
                os.rmdir(target_dir)


class StoreDownloadsubmissionFileTest(WsTestCase):
    def test_get_not_exists(self):
        response = self.fetch(API_URL_PREFIX + f"/store/download/submissionfile/I_DO_EXIST2/0", method='GET',
                              headers={'Cookie': self.login_admin()})
        self.assertEqual(400, response.code)
        self.assertEqual('Submission File not found', response.reason)


test_sb_file = """/begin_header
/identifier_product_doi=10.5067/SeaBASS/SOCCOM/DATA001
/received=20180720
/investigators=Emmanuel_Boss,Lynne_Talley
/affiliations=UMaine,Scripps
/contact=emmanuel.boss@maine.edu
/experiment=SOCCOM
/cruise=ACE_2017
!/cruise=ACE
/station=NA
/data_file_name=ACE-HPLC-Pigments-20171019-to-Lynne.xlsx
/documents=SOCCOM_ACE_HPLC.pdf,HPLC_method_summary.pdf
/calibration_files=SOCCOM_ACE_HPLC.pdf
/data_type=pigment
/data_status=preliminary
/start_date=20170111
/end_date=20170111
/start_time=11:05:00[GMT]
/end_time=11:05:00[GMT]
/north_latitude=-54.8519[DEG]
/south_latitude=-54.8519[DEG]
/east_longitude=95.7697[DEG]
/west_longitude=95.7697[DEG]
/water_depth=NA
!
! HPLC samples analyzed by Crystal Thomas at NASA GSFC
!
! COMMENTS
! Reference_file = ACE-HPLC-Pigments-20171019-to-Lynne.xlsx
! Date_processed = 04/05/17
! Name_of_water_body = Indian Ocean
! Water_type = Open Ocean
! CCHDO_EXPO = RUB320161220
! Quality codes (following CCHDO guidelines):
!     0. No quality check performed on measurement.
!     1. Sample for this measurement was drawn from water bottle but analysis not received.
!     2. Acceptable measurement.
!     3. Questionable measurement.
!     4. Bad measurement.
!     5. Not reported.
!     6. Mean of replicate measurements (Number of replicates is specified in column bincount).
!     9. Sample not drawn for this measurement from this bottle.
!
! MV_CHL_A includes allomers and epimers
! No replicates available.
!
/missing=-9999
/below_detection_limit=-8888
/delimiter=comma
/fields=year,month,day,sdy,time,sample,water_depth,lon,lat,station,bottle,depth,Tot_Chl_a,Tot_Chl_b,But-fuco,Hex-fuco,Allo,Diadino,Diato,Fuco,Perid,Chlide_a,Chl_c1c2,Chl_c3,Neo,Viola,Phytin_a,Phide_a,Pras,volfilt,quality
/units=yyyy,mo,dd,ddd,hh:mm:ss,none,m,degrees,degrees,none,none,m,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,mg/m^3,l,none
/end_header
2017,1,11,11,11:05:00,18,-9999,95.7697,-54.8519,20,3,100,0.2672,0.0114,0.0207,0.0687,0.0013,0.0075,-9999,0.1065,0.0039,-9999,0.0538,0.0397,0.0018,-9999,0.0108,0.0322,0.0025,2,0
2017,1,11,11,11:05:00,17,-9999,95.7697,-54.8519,20,6,80,0.2675,0.0130,0.0233,0.0952,-9999,0.0104,-9999,0.0897,0.0036,-9999,0.0566,0.0380,0.0017,-9999,0.0140,0.0226,0.0026,2,0
2017,1,11,11,11:05:00,16,-9999,95.7697,-54.8519,20,7,71,0.2514,0.0112,0.0221,0.0924,-9999,0.0130,-9999,0.0801,0.0058,0.0042,0.0567,0.0336,0.0016,0.0013,0.0146,0.0233,0.0024,2,0
2017,1,11,11,11:05:00,15,-9999,95.7697,-54.8519,20,12,61,0.2411,0.0091,0.0203,0.0930,-9999,0.0160,0.0013,0.0710,0.0089,0.0049,0.0545,0.0274,0.0013,0.0010,0.0145,0.0276,0.0020,2,0
2017,1,11,11,11:05:00,14,-9999,95.7697,-54.8519,20,14,46,0.1528,0.0074,0.0146,0.0724,-9999,0.0132,0.0012,0.0522,0.0050,-9999,0.0419,0.0221,0.0009,-9999,0.0329,0.0271,0.0014,2,0
2017,1,11,11,11:05:00,13,-9999,95.7697,-54.8519,20,18,31,0.1983,0.0073,0.0152,0.0748,-9999,0.0179,0.0016,0.0565,0.0080,0.0067,0.0454,0.0244,0.0010,-9999,0.0117,0.0227,0.0012,2,0
2017,1,11,11,11:05:00,12,-9999,95.7697,-54.8519,20,19,18,0.1696,0.0071,0.0125,0.0652,-9999,0.0130,0.0013,0.0497,0.0048,0.0057,0.0413,0.0231,0.0009,-9999,0.0149,0.0247,0.0012,2,0
2017,1,11,11,11:05:00,11,-9999,95.7697,-54.8519,20,24,4,0.1461,0.0064,0.0116,0.0624,-9999,0.0116,0.0014,0.0439,0.0059,-9999,0.0353,0.0195,0.0007,-9999,0.0185,0.0216,0.0010,2,0
"""


class ValidateSubmissionTest(WsTestCase):

    def test_post_as_admin(self):
        cookie = self.login_admin()

        try:
            data = test_sb_file
            send = {'data': data}
            import json
            body = json.dumps(send).encode('utf-8')

            response = self.fetch(API_URL_PREFIX + "/store/upload/submission/validate",
                                  method='POST',
                                  body=body,
                                  headers={"Cookie": cookie})
            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)
            actual_response_data = tornado.escape.json_decode(response.body)
            self.assertIsInstance(actual_response_data, dict)
            self.assertIn("status", actual_response_data)
            self.assertIn("OK", actual_response_data["status"])
        finally:
            self.logout_admin()

    def test_post_not_logged_in(self):
        dataset = new_test_dataset(13)
        data = {'data': dataset.to_dict()}
        body = tornado.escape.json_encode(data)
        response = self.fetch(API_URL_PREFIX + "/store/upload/submission/validate", method='POST', body=body)
        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)


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
        mtype = None
        wlmode = None
        shallow = None
        pmode = None
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

        query = 'pgroup=chl_a&pgroup=a_pig'

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

        query = 'pname=BACTABB&pname=bottle'

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

    def test_delete_not_logged_in(self):
        dataset_ref = add_dataset(self.ctx, new_test_dataset(0))
        dataset_id = dataset_ref.id
        response = self.fetch(API_URL_PREFIX + f"/datasets/{dataset_id}",
                              method='DELETE')
        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operation.', response.reason)

    def test_delete(self):
        cookie = self.login_admin()

        try:
            dataset_ref = add_dataset(self.ctx, new_test_dataset(0))
            dataset_id = dataset_ref.id
            response = self.fetch(API_URL_PREFIX + f"/datasets/{dataset_id}",
                                  method='DELETE',
                                  headers={"Cookie": cookie})
            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            response = self.fetch(API_URL_PREFIX + f"/datasets/{dataset_id}",
                                  method='DELETE',
                                  headers={"Cookie": cookie})
            self.assertEqual(404, response.code)
            self.assertEqual(f'Dataset with ID {dataset_id} not found', response.reason)
        finally:
            self.logout_admin()


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

    def test_post_admin(self):
        cookie = self.login_admin()

        try:
            dataset_ref = add_dataset(self.ctx, new_test_dataset(42))
            dataset_id = dataset_ref.id

            expected_qc_info = QcInfo(QC_STATUS_VALIDATED,
                                      dict(by='Illaria',
                                           when="2019-02-01",
                                           doc_files=["qc-report.docx"]))
            body = tornado.escape.json_encode(expected_qc_info.to_dict())
            response = self.fetch(API_URL_PREFIX + f"/datasets/{dataset_id}/qcinfo", method='POST', body=body,
                                  headers={"Cookie": cookie})
            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

            actual_qc_info = get_dataset_qc_info(self.ctx, dataset_id)
            self.assertEqual(expected_qc_info, actual_qc_info)
        finally:
            self.logout_admin()

    def test_post_no_admin(self):
        dataset_ref = add_dataset(self.ctx, new_test_dataset(42))
        dataset_id = dataset_ref.id

        expected_qc_info = QcInfo(QC_STATUS_VALIDATED,
                                  dict(by='Illaria',
                                       when="2019-02-01",
                                       doc_files=["qc-report.docx"]))
        body = tornado.escape.json_encode(expected_qc_info.to_dict())
        response = self.fetch(API_URL_PREFIX + f"/datasets/{dataset_id}/qcinfo", method='POST', body=body)
        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operation.', response.reason)


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


class HandleUsersTest(WsTestCase):

    def test_add_no_admin(self):
        data = {
            'name': 'hinz',
            'first_name': 'Hinz',
            'last_name': 'Kunz',
            'password': 'lappig9',
            'email': None,
            'phone': None,
            'roles': ['admin']
        }
        body = tornado.escape.json_encode(data)

        response = self.fetch(API_URL_PREFIX + "/users", method='POST', body=body)
        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test_add_admin(self):
        cookie = self.login_admin()

        try:
            data = {
                'name': 'hinz',
                'first_name': 'Hinz',
                'last_name': 'Kunz',
                'password': 'lappig9',
                'email': None,
                'phone': None,
                'roles': ['admin']
            }
            body = tornado.escape.json_encode(data)

            response = self.fetch(API_URL_PREFIX + "/users", method='POST', body=body, headers={"Cookie": cookie})
            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

        finally:
            self.logout_admin()


class LoginUsersTest(WsTestCase):

    def test_login_existing_user(self):
        user = User(name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                    first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

        create_user(self.ctx, user)

        credentials = {'username': "scott", 'password': "tiger", 'client_version': MIN_CLIENT_VERSION}
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='POST', body=body)

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        expected_response_data = {
            'id': '',
            'name': 'scott',
            'email': 'bruce.scott@gmail.com',
            'first_name': 'Bruce',
            'last_name': 'Scott',
            'phone': '+34 5678901234',
            'roles': ['submit', 'admin']
        }

        actual_response_data = tornado.escape.json_decode(response.body)
        actual_response_data['id'] = ''
        self.assertEqual(expected_response_data, actual_response_data)

    def test_login_existing_user_wrong_password(self):
        user = User(name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                    first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

        create_user(self.ctx, user)

        credentials = {'username': "scott", 'password': "lion", 'client_version': MIN_CLIENT_VERSION}
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='POST', body=body)

        self.assertEqual(401, response.code)
        self.assertEqual('Unknown username or password', response.reason)

    def test_login_unknown_user(self):
        credentials = {'username': "malcolm", 'password': "rattenloch", 'client_version': MIN_CLIENT_VERSION}

        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='POST', body=body)

        self.assertEqual(401, response.code)
        self.assertEqual('Unknown username or password', response.reason)

    def test_login_too_low_client_version(self):
        res = self.login_admin_no_assert(client_version="0.1")
        self.assertEqual(409, res.code)

    def test_change_passwd(self):
        cookie = self.login_admin()

        user = User(name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                    first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

        create_user(self.ctx, user)

        credentials = dict(username="scott", oldpassword="eocdb_chef", newpassword1='sdfv', newpassword2='sdfv')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        expected_response_data = {'id': '', 'message': "User scott's password updated."}

        actual_response_data = tornado.escape.json_decode(response.body)
        actual_response_data['id'] = ''
        self.assertEqual(expected_response_data, actual_response_data)

    def test_change_own_passwd(self):
        cookie = self.login_admin()

        credentials = dict(username="submit", oldpassword="eocdb_chef", newpassword1='submit2', newpassword2='submit2')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        # user = get_user_by_name(ctx=self.ctx, user_name='submit', retain_password=True)

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        # self.assertEqual('submit2', user['password'])

    def test_change_own_passwd_wrong_old_passwd(self):
        cookie = self.login_submit()

        credentials = dict(username="submit", oldpassword="submit22", newpassword1='submit2', newpassword2='submit2')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        # user = get_user_by_name(ctx=self.ctx, user_name='submit', retain_password=True)

        self.assertEqual(403, response.code)
        self.assertEqual('Current password does not match.', response.reason)

    def test_change_passwd_as_admin(self):
        cookie = self.login_admin()

        credentials = dict(username='submit', oldpassword="eocdb_chef", newpassword1='submit2', newpassword2='submit2')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        # user = get_user_by_name(ctx=self.ctx, user_name='submit', retain_password=True)

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        # self.assertEqual('submit2', user['password'])

    def test_change_passwd_from_somone_else_without_rights(self):
        cookie = self.login_submit()

        user = User(name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                    first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

        create_user(self.ctx, user)

        credentials = dict(username="scott", oldpassword="tiger", newpassword1='sdfv', newpassword2='sdfv')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        self.assertEqual(403, response.code)
        self.assertEqual('Current password does not match.', response.reason)


class LogoutUsersTest(WsTestCase):

    def test_get_no_user_logged_in(self):
        response = self.fetch(API_URL_PREFIX + "/users/logout", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

    def test_get(self):
        self.login_admin()

        response = self.fetch(API_URL_PREFIX + "/users/logout", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)


class GetUserByNameTest(WsTestCase):

    def test_get(self):
        name = 'chef'

        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='GET', headers={"Cookie": self.login_admin()})
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual("chef", actual_response_data['name'])
        self.assertEquals(['submit', 'admin'], actual_response_data['roles'])

    def test_get_not_logged_in(self):
        name = 'chef'
        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='GET')
        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test_get_not_own_user_name(self):
        name = 'chef'
        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='GET', headers={"Cookie": self.login_submit()})
        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operations on user chef.', response.reason)

    def test_put(self):
        user = DbUser(
            id_='asdoökvn',
            name="submit",
            password="submit",
            first_name='Submit',
            last_name="Submit",
            email="sdfv",
            phone="",
            roles=["submit", ]
        )

        name = 'chef'

        data = user.to_dict()

        body = tornado.escape.json_encode(data)

        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='PUT', body=body,
                              headers={"Cookie": self.login_admin()})
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        expected_response_data = {'message': 'User chef updated'}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)

    def test_put_not_logged_in(self):
        name = 'chef'
        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='PUT', body=tornado.escape.json_encode({}))
        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test_put_not_own_user_name(self):
        user = DbUser(
            id_='asdoökvn',
            name="helge",
            password="submit",
            first_name='Submit',
            last_name="Submit",
            email="sdfv",
            phone="",
            roles=["submit", ]
        )

        name = 'chef'

        data = user.to_dict()

        body = tornado.escape.json_encode(data)
        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='PUT', body=body,
                              headers={"Cookie": self.login_submit()})
        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operations on user chef.', response.reason)

    def test_delete(self):
        user = DbUser(
            id_='asdoökvnd',
            name="helge",
            password="submit",
            first_name='Submit',
            last_name="Submit",
            email="sdfv",
            phone="",
            roles=["submit", ]
        )
        create_user(self.ctx, user=user)

        response = self.fetch(API_URL_PREFIX + "/users/helge", method='DELETE', headers={'Cookie': self.login_admin()})
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        expected_response_data = {'message': 'User helge deleted'}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)

    def test_delete_not_logged_in(self):
        name = 'chef'

        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='DELETE')
        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test_delete_not_admin(self):
        name = 'chef'

        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='DELETE',
                              headers={"Cookie": self.login_submit()})
        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operation.', response.reason)


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
