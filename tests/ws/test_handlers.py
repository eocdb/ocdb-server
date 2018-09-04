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

        self.assertEqual([{'records': [[58.1, 11.1, 0.3],
                                       [58.4, 11.4, 0.2],
                                       [58.5, 10.9, 0.7],
                                       [58.2, 10.8, 0.2],
                                       [58.9, 11.2, 0.1]]}],
                         json.loads(response.body))

    def test_fetch_query_succeeds_no_results(self):
        response = self.fetch('/eocdb/api/measurements?query=bert')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        self.assertEqual([{'records': []}],
                         json.loads(response.body))

    def test_fetch_query_fails(self):
        response = self.fetch('/eocdb/api/measurements?query=trigger_error')
        self.assertEqual(500, response.code)
        self.assertEqual('Internal Server Error', response.reason)
        self.assertEqual({'error': {'code': 500, 'message': 'Internal Server Error'}},
                         json.loads(response.body))
