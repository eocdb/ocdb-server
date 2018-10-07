import unittest

from tests.ws.helpers import RequestParamsMock

from eocdb.ws.errors import WsBadRequestError
from eocdb.ws.reqparams import RequestParams


class RequestParamsTest(unittest.TestCase):
    def test_to_bool(self):
        self.assertEqual(True, RequestParams.to_bool('x', 'true'))
        self.assertEqual(True, RequestParams.to_bool('x', 'True'))
        self.assertEqual(True, RequestParams.to_bool('x', '1'))
        self.assertEqual(False, RequestParams.to_bool('x', 'false'))
        self.assertEqual(False, RequestParams.to_bool('x', 'False'))
        self.assertEqual(False, RequestParams.to_bool('x', '0'))
        with self.assertRaises(WsBadRequestError):
            RequestParams.to_bool('x', None)
        with self.assertRaises(WsBadRequestError):
            RequestParams.to_bool('x', 'bibo')

    def test_to_int(self):
        self.assertEqual(2123, RequestParams.to_int('x', '2123', minimum=0, maximum=5000))
        with self.assertRaises(WsBadRequestError):
            RequestParams.to_int('x', None)
        with self.assertRaises(WsBadRequestError):
            RequestParams.to_int('x', 'bibo')
        with self.assertRaises(WsBadRequestError):
            RequestParams.to_float('x', '12', minimum=20)
        with self.assertRaises(WsBadRequestError):
            RequestParams.to_float('x', '12', maximum=10)

    def test_to_float(self):
        self.assertEqual(-0.2, RequestParams.to_float('x', '-0.2', minimum=-1.0, maximum=1.0))
        with self.assertRaises(WsBadRequestError):
            RequestParams.to_float('x', None)
        with self.assertRaises(WsBadRequestError):
            RequestParams.to_float('x', 'bibo')
        with self.assertRaises(WsBadRequestError):
            RequestParams.to_float('x', '2.5', minimum=3.0)
        with self.assertRaises(WsBadRequestError):
            RequestParams.to_float('x', '2.5', maximum=2.0)

    def test_get_query_argument(self):
        rp = RequestParamsMock()
        self.assertEqual('bert', rp.get_query_argument('s', 'bert'))
        self.assertEqual(234, rp.get_query_argument_int('i', 234))
        self.assertEqual(0.2, rp.get_query_argument_float('f', 0.2))

        rp = RequestParamsMock(s='bibo', b='1', i='465', f='0.1')
        self.assertEqual('bibo', rp.get_query_argument('s', None))
        self.assertEqual(True, rp.get_query_argument_bool('b', None))
        self.assertEqual(465, rp.get_query_argument_int('i', None))
        self.assertEqual(465., rp.get_query_argument_float('i', None))
        self.assertEqual(0.1, rp.get_query_argument_float('f', None))
