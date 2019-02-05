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

from eocdb.core.models.qc_info import QcInfo, QC_INFO_STATUS_PASSED
from eocdb.ws.app import new_application
from eocdb.ws.controllers.datasets import add_dataset, find_datasets, get_dataset_by_id_strict, get_dataset_qc_info
from eocdb.ws.handlers import API_URL_PREFIX
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
        self.assertEqual("0.1.0-dev.7", result["info"].get("version"))
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


class StoreUploadTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_post(self):
        # TODO (generated): set data for request body to reasonable value
        data = None
        body = data

        response = self.fetch(API_URL_PREFIX + "/store/upload", method='POST', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
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
        geojson=False
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
        dataset.attributes = ['chl_a']
        add_dataset(self.ctx, dataset)
        add_dataset(self.ctx, new_test_dataset(1))
        dataset = new_test_dataset(2)
        dataset.attributes = ['a_pig']
        add_dataset(self.ctx, dataset)
        dataset = new_test_dataset(3)
        dataset.attributes = ['b_part']
        add_dataset(self.ctx, dataset)

        query = 'mtype=all&wlmode=all&shallow=no&pmode=contains&pgroup=chl_a&pgroup=a_pig'

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
        expected_response_data = {'result': None, 'status': 'waiting'}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)

    def test_post(self):
        dataset_ref = add_dataset(self.ctx, new_test_dataset(42))
        dataset_id = dataset_ref.id

        expected_qc_info = QcInfo(QC_INFO_STATUS_PASSED,
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
