import unittest

from ocdb.ws.errors import WsBadRequestError
from ocdb.ws.utils import ensure_valid_submission_id, ensure_valid_path


class UtilsTest(unittest.TestCase):
    def test_ensure_valid_submission_id(self):
        submission_id = "tintin"
        ensure_valid_submission_id(submission_id)

        submission_id = "tintin\nhelge"
        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id(submission_id)

        self.assertEqual("HTTP 400: Please use only alphanumeric characters or underscore in your submission id.", str(e.exception))

        submission_id = "/tintin"
        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id(submission_id)

        self.assertEqual("HTTP 400: Please use only alphanumeric characters or underscore in your submission id.", str(e.exception))

        submission_id = "./tintin"
        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id(submission_id)

        self.assertEqual("HTTP 400: Please use only alphanumeric characters or underscore in your submission id.", str(e.exception))

        submission_id = "./tintin\n/."
        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id(submission_id)

        self.assertEqual("HTTP 400: Please use only alphanumeric characters or underscore in your submission id.", str(e.exception))

        submission_id = "tintin##"
        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_submission_id(submission_id)

        self.assertEqual("HTTP 400: Please use only alphanumeric characters or underscore in your submission id.", str(e.exception))

    def test_ensure_valid_path(self):
        path = "test/bla/tintin"
        ensure_valid_path(path)

        msg = 'HTTP 400: Please provide the path as format: AFFILIATION (acronym)/EXPERIMENT/CRUISE and use ' \
              'characters, numbers and underscores only.'

        path = "/test/bla/tintin"

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path(path)

        self.assertEqual(msg, str(e.exception))

        path = "/te.st/bla/tintin"

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path(path)

        self.assertEqual(msg, str(e.exception))

        path = "../test/bla/tintin/"

        with self.assertRaises(WsBadRequestError) as e:
            ensure_valid_path(path)

        self.assertEqual(msg, str(e.exception))

