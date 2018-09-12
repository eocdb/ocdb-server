import json

from tornado.testing import AsyncHTTPTestCase

from eocdb.ws.app import new_application
from tests.ws.helpers import new_test_service_context


# For usage of the tornado.testing.AsyncHTTPTestCase see http://www.tornadoweb.org/en/stable/testing.html

class HandlersTest(AsyncHTTPTestCase):
    def get_app(self):
        application = new_application()
        application.ws_context = new_test_service_context()
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

        self.assertEqual([{'attributes': ['lon', 'lat', 'chl', 'depth'],
                           'geo_locations': [{'lat': 16.45, 'lon': -34.7}],
                           'metadata': {'contact': 'ernie@sesame_street.com',
                           'experiment': 'Counting pigments',
                           'name': 'ernie'},
                           'records': [[-34.7, 16.45, 0.345, 12.2],
                                       [-34.7, 16.45, 0.298, 14.6],
                                       [-34.7, 16.45, 0.307, 18.3],
                                       [-34.7, 16.45, 0.164, 22.6],
                                       [-34.7, 16.45, 0.108, 29.8]],
                           'times': ['2017-05-22T08:32:44',
                                     '2017-05-22T08:32:48',
                                     '2017-05-22T08:32:52',
                                     '2017-05-22T08:32:56',
                                     '2017-05-22T08:33:00']}],
                         json.loads(response.body))

    def test_fetch_query_succeeds_no_results(self):
        response = self.fetch('/eocdb/api/measurements?query=bert')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        self.assertEqual([], json.loads(response.body))

    def test_fetch_query_fails(self):
        response = self.fetch('/eocdb/api/measurements?query=trigger_error')
        self.assertEqual(500, response.code)
        self.assertEqual('Internal Server Error', response.reason)
        self.assertEqual({'error': {'code': 500, 'message': 'Internal Server Error'}},
                         json.loads(response.body))
