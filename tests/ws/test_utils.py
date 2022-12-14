import unittest

from ocdb.ws.errors import WsBadRequestError
from ocdb.ws.utils import ensure_valid_submission_id, ensure_valid_path


class UtilsTest(unittest.TestCase):
    def test_ensure_valid_submission_id(self):
        expected_msg = "HTTP 400: Please use only alphanumeric characters, underscore or minus sign in your " \
                       "submission id. At least one letter must be used."
        self.assertTrue(ensure_valid_submission_id("tintin"))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id("tintin\nhelge")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id("/tintin")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id(".tintin")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id("tintin\n")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id("tintin#")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id(" ")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id("-")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id("_")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id("")
        self.assertEqual(expected_msg, str(e.exception))

    def test_ensure_valid_path(self):
        expected_msg = 'HTTP 400: Provide the path as follows: name/name/name (AFFILIATION/EXPERIMENT/CRUISE). ' \
                       'Each name must contain at least one letter. ' \
                       'Use characters, numbers, minus and underscores only.'

        self.assertTrue(ensure_valid_path("ab/cd/ef"))
        self.assertTrue(ensure_valid_path("a3-_b/c4_-d/-_5ef"))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("/cd/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab//ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/cd/")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("_/cd/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/_/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/cd/_")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("-/cd/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/-/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/cd/-")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("1/cd/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/2/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/cd/3")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("/ab/cd/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/cd/ef/")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("a.b/cd/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/c.d/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/cd/e.f")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("../test/bla/tintin/")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("-_43_-/cd/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/-_43_-/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/cd/-_43_-")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path(" ab/cd/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/c d/ef")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("ab/cd/ef ")
        self.assertEqual(expected_msg, str(e.exception))

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path("//")
        self.assertEqual(expected_msg, str(e.exception))
