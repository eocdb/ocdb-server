import unittest

from tornado.web import HTTPError

from ocdb.ws.errors import WsError, WsConfigError, WsBadRequestError, WsResourceNotFoundError


class ErrorsTest(unittest.TestCase):
    def test_base_error(self):
        self.assertIsInstance(WsError(''), HTTPError)
        self.assertEqual(500, WsError('').status_code)
        self.assertEqual(503, WsError('', status_code=503).status_code)

    def test_config_error(self):
        self.assertIsInstance(WsConfigError(''), WsError)
        self.assertEqual(500, WsConfigError('').status_code)

    def test_bad_request_error(self):
        self.assertIsInstance(WsBadRequestError(''), WsError)
        self.assertEqual(400, WsBadRequestError('').status_code)

    def test_resource_not_found_error(self):
        self.assertIsInstance(WsResourceNotFoundError(''), WsError)
        self.assertEqual(404, WsResourceNotFoundError('').status_code)
