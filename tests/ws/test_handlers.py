import json

from tornado.testing import AsyncHTTPTestCase

from eocdb.ws.app import new_application
from tests.ws.helpers import new_test_service_context


# For usage of the tornado.testing.AsyncHTTPTestCase see http://www.tornadoweb.org/en/stable/testing.html

class HandlersTest(AsyncHTTPTestCase):
    def get_app(self):
        application = new_application()
        application.service_context = new_test_service_context()
        return application

    def test_fetch_base(self):
        response = self.fetch('/')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        self.assertEqual(dict(name='eocdb-server',
                              version='0.1.0',
                              description='EUMETSAT Ocean Colour In-Situ Database Server'),
                         json.loads(response.body))

    def test_fetch_query_succeeds(self):
        response = self.fetch('/eocdb/api/measurements?query=ernie')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        self.assertEqual(dict(id=[1, 2, 3, 4, 5],
                              lon=[58.1, 58.4, 58.5, 58.2, 58.9],
                              lat=[11.1, 11.4, 10.9, 10.8, 11.2],
                              chl=[0.3, 0.2, 0.7, 0.2, 0.1]),
                         json.loads(response.body))

    def test_fetch_query_fails(self):
        response = self.fetch('/eocdb/api/measurements?query=bert')
        self.assertEqual(400, response.code)
        self.assertEqual('The only valid query string is "ernie"', response.reason)
        self.assertEqual(dict(error=dict(code=400, message='The only valid query string is "ernie"')),
                         json.loads(response.body))

    # def test_fetch_wmts_capabilities(self):
    #     response = self.fetch('/xcube/wmts/1.0.0/WMTSCapabilities.xml')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_wmts_tile(self):
    #     response = self.fetch('/xcube/wmts/1.0.0/tile/demo/conc_chl/0/0/0.png')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_wmts_tile_with_params(self):
    #     response = self.fetch('/xcube/wmts/1.0.0/tile/demo/conc_chl/0/0/0.png?time=current&cbar=jet')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_dataset_tile(self):
    #     response = self.fetch('/xcube/tile/demo/conc_chl/0/0/0.png')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_dataset_tile_with_params(self):
    #     response = self.fetch('/xcube/tile/demo/conc_chl/0/0/0.png?time=current&cbar=jet')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_dataset_tile_grid_ol4_json(self):
    #     response = self.fetch('/xcube/tilegrid/demo/conc_chl/ol4.json')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_dataset_tile_grid_cesium_json(self):
    #     response = self.fetch('/xcube/tilegrid/demo/conc_chl/cesium.json')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_ne2_tile(self):
    #     response = self.fetch('/xcube/tile/ne2/0/0/0.jpg')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_ne2_tile_grid(self):
    #     response = self.fetch('/xcube/tilegrid/ne2/ol4.json')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_datasets_json(self):
    #     response = self.fetch('/xcube/datasets.json')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_variables_json(self):
    #     response = self.fetch('/xcube/variables/demo.json')
    #     self.assertEqual(200, response.code)
    #     response = self.fetch('/xcube/variables/demo.json?client=ol4')
    #     self.assertEqual(200, response.code)
    #     response = self.fetch('/xcube/variables/demo.json?client=cesium')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_coords_json(self):
    #     response = self.fetch('/xcube/coords/demo/time.json')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_color_bars_json(self):
    #     response = self.fetch('/xcube/colorbars.json')
    #     self.assertEqual(200, response.code)
    #
    # def test_fetch_color_bars_html(self):
    #     response = self.fetch('/xcube/colorbars.html')
    #     self.assertEqual(200, response.code)
