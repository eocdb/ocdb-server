from datetime import datetime
from unittest import TestCase

from eocdb.core.db.db_submission_file import DbSubmissionFile


class DbSubmissionFileTest(TestCase):

    def test_to_dict(self):
        date = datetime(2017, 3, 22, 11, 14, 33)
        sf = DbSubmissionFile(submission_id="the_file_id",
                              date=date,
                              user_id="abcdefghijockel")

        self.assertEqual({'date': datetime(2017, 3, 22, 11, 14, 33),
                          'id': None,
                          'submission_id': 'the_file_id',
                          'user_id': 'abcdefghijockel'}, sf.to_dict())