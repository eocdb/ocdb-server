from unittest import TestCase

from eocdb.core.db.submission_file import SubmissionFile


class SubmissionFileTest(TestCase):

    def test_to_dict(self):
        sf = SubmissionFile("the_file_id")

        self.assertEqual({'id': None,
                          'submission_id': 'the_file_id'}, sf.to_dict())