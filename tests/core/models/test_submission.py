from datetime import datetime
from unittest import TestCase

from ocdb.core.models import QC_STATUS_SUBMITTED, QC_STATUS_VALIDATED
from ocdb.core.models.submission import Submission
from ocdb.core.models.submission_file_ref import SubmissionFileRef
from tests.helpers import NOW


class SubmissionTest(TestCase):

    def test_to_dict(self):
        sfrs = [SubmissionFileRef(submission_id="12", created_date=NOW, index=7, filename="bla", filetype="blubb", status="who_knows")]
        submission = Submission(submission_id="submit_me",
                                user_id="6789",
                                date=datetime(2016, 2, 21, 10, 13, 32),
                                status=QC_STATUS_SUBMITTED,
                                qc_status='OK',
                                publication_date=datetime(2016, 2, 21, 10, 13, 32),
                                updated_date=datetime(2016, 2, 21, 10, 13, 32),
                                allow_publication=True,
                                file_refs=sfrs)

        self.assertEqual({'date': '2016-02-21 10:13:32',
                          'file_refs': [{'filename': 'bla',
                                         'filetype': 'blubb',
                                         'created_date': '2009-08-07 06:05:04',
                                         'index': 7,
                                         'status': 'who_knows',
                                         'submission_id': '12'}],
                          'qc_status': 'OK',
                          'status': QC_STATUS_SUBMITTED,
                          'publication_date': '2016-02-21 10:13:32',
                          'updated_date': '2016-02-21 10:13:32',
                          'allow_publication': True,
                          'submission_id': 'submit_me',
                          'user_id': "6789"}, submission.to_dict())

    def test_from_dict(self):
        sm_dict = {"submission_id": "ttzzrreeww",
                   'user_id': "834569982763",
                   'date': '2015-01-20 09:12:31',
                   'status': QC_STATUS_VALIDATED,
                   'qc_status': 'WARNING',
                   'allow_publication': True,
                   'publication_date': '2015-01-20 09:12:31',
                   'updated_date': '2015-01-20 09:12:31',
                   'file_refs': [{'filename': 'jepp',
                                  'filetype': 'holla',
                                  'created_date': '2015-01-20 09:12:31',
                                  'index': 8,
                                  'status': 'happy',
                                  'submission_id': 'argonaut'}],
                   }

        submission = Submission.from_dict(sm_dict)

        self.assertEqual(sm_dict, submission.to_dict())
