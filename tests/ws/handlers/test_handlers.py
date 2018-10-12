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
import urllib.parse

import tornado.escape
import tornado.testing

from eocdb.ws.app import new_application
from eocdb.ws.controllers.datasets import add_dataset, find_datasets
from ..helpers import new_test_service_context, new_dataset


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
        response = self.fetch(f"/service/info", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        result = tornado.escape.json_decode(response.body)
        self.assertIn("openapi", result)
        self.assertEqual("3.0.0", result["openapi"])
        self.assertIn("info", result)
        self.assertEqual(dict(title="eocdb-server",
                              version="0.1.0-dev.1",
                              description="Web Service API for the EUMETSAT Ocean Colour In-Situ Database\n",
                              contact=dict(email="eocdb@eumetsat.eu"),
                              license=dict(name="MIT",
                                           url="https://opensource.org/licenses/MIT")),
                         result["info"])


class StoreInfoTest(WsTestCase):

    def test_get(self):
        response = self.fetch(f"/store/info", method='GET')
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

        response = self.fetch(f"/store/upload", method='POST', body=body)
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
        query = urllib.parse.urlencode(
            dict(expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype, wlmode=wlmode, shallow=shallow,
                 pmode=pmode, pgroup=pgroup, pname=pname, docs=docs))

        response = self.fetch(f"/store/download?{query}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = None
        actual_response_data = response.body
        self.assertEqual(expected_response_data, actual_response_data)


class DatasetsTest(WsTestCase):

    def test_get(self):
        add_dataset(self.ctx, new_dataset(0))
        add_dataset(self.ctx, new_dataset(1))
        add_dataset(self.ctx, new_dataset(2))
        add_dataset(self.ctx, new_dataset(3))

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

        response = self.fetch(f"/datasets?{query}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertIn("total_count", actual_response_data)
        self.assertEqual(4, actual_response_data["total_count"])

    def test_put(self):
        dry = 0

        data = new_dataset(13).to_dict()
        body = tornado.escape.json_encode(data)
        query = urllib.parse.urlencode(dict(dry=dry))

        response = self.fetch(f"/datasets?{query}", method='PUT', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        datasets = find_datasets(self.ctx)
        self.assertEqual(1, datasets.total_count)

    @unittest.skip('not implemented yet')
    def test_post(self):
        # TODO (generated): set query parameter(s) to reasonable value(s)
        dry = None

        # TODO (generated): set data for request body to reasonable value
        data = {}
        body = tornado.escape.json_encode(data)
        query = urllib.parse.urlencode(dict(dry=dry))

        response = self.fetch(f"/datasets?{query}", method='POST', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)


class DatasetsIdTest(WsTestCase):
    @property
    def ctx(self):
        return self._app.ws_context

    def test_get(self):
        add_dataset(self.ctx, new_dataset(0))
        datasets = find_datasets(self.ctx)
        dataset_ref = datasets.datasets[0]

        id = dataset_ref.id
        response = self.fetch(f"/datasets/{id}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertIn("id", actual_response_data)
        self.assertEqual(id, actual_response_data["id"])

        id = "gnarz-foop"
        response = self.fetch(f"/datasets/{id}", method='GET')
        self.assertEqual(404, response.code)
        self.assertEqual('dataset with ID gnarz-foop not found', response.reason)

    @unittest.skip('not implemented yet')
    def test_delete(self):
        # TODO (generated): set path parameter(s) to reasonable value(s)
        id = None

        response = self.fetch(f"/datasets/{id}", method='DELETE')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)


class DatasetsAffilProjectCruiseTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_get(self):
        # TODO (generated): set path parameter(s) to reasonable value(s)
        affil = None
        project = None
        cruise = None

        response = self.fetch(f"/datasets/{affil}/{project}/{cruise}", method='GET')
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

        response = self.fetch(f"/datasets/{affil}/{project}/{cruise}/{name}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = None
        actual_response_data = response.body
        self.assertEqual(expected_response_data, actual_response_data)


class DocfilesTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_put(self):
        # TODO (generated): set data for request body to reasonable value
        data = None
        body = data

        response = self.fetch(f"/docfiles", method='PUT', body=body)
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

        response = self.fetch(f"/docfiles", method='POST', body=body)
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

        response = self.fetch(f"/docfiles/{affil}/{project}/{cruise}", method='GET')
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

        response = self.fetch(f"/docfiles/{affil}/{project}/{cruise}/{name}", method='GET')
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

        response = self.fetch(f"/docfiles/{affil}/{project}/{cruise}/{name}", method='DELETE')
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

        response = self.fetch(f"/users", method='POST', body=body)
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)


class UsersLoginTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_get(self):
        # TODO (generated): set query parameter(s) to reasonable value(s)
        username = None
        password = None
        query = urllib.parse.urlencode(dict(username=username, password=password))

        response = self.fetch(f"/users/login?{query}", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = None
        actual_response_data = response.body
        self.assertEqual(expected_response_data, actual_response_data)


class UsersLogoutTest(WsTestCase):

    @unittest.skip('not implemented yet')
    def test_get(self):
        response = self.fetch(f"/users/logout", method='GET')
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

        response = self.fetch(f"/users/{id}", method='GET')
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

        response = self.fetch(f"/users/{id}", method='PUT', body=body)
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

        response = self.fetch(f"/users/{id}", method='DELETE')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        # TODO (generated): set expected_response correctly
        expected_response_data = {}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)
