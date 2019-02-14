from datetime import datetime
from unittest import TestCase

from eocdb.core.models import QC_STATUS_SUBMITTED, QC_STATUS_VALIDATED
from eocdb.core.models.submission import Submission
from eocdb.core.models.submission_file_ref import SubmissionFileRef


class SubmissionTest(TestCase):

    def test_to_dict(self):
        sfrs = [SubmissionFileRef(submission_id="12", index=7, filename="bla", filetype="blubb", status="who_knows")]
        submission = Submission(id="ei_dih",
                                submission_id="submit_me",
                                user_id=6789,
                                date=datetime(2016, 2, 21, 10, 13, 32),
                                status=QC_STATUS_SUBMITTED,
                                qc_status='OK',
                                file_refs=sfrs)

        self.assertEqual({'date': datetime(2016, 2, 21, 10, 13, 32),
                          'file_refs': [{'filename': 'bla',
                                         'filetype': 'blubb',
                                         'index': 7,
                                         'status': 'who_knows',
                                         'submission_id': '12'}],
                          'id': 'ei_dih',
                          'qc_status': 'OK',
                          'status': QC_STATUS_SUBMITTED,
                          'submission_id': 'submit_me',
                          'user_id': 6789}, submission.to_dict())

    def test_from_dict(self):
        sm_dict = {"id": "3556tr",
                   "submission_id": "ttzzrreeww",
                   'user_id': 834569982763,
                   'date': datetime(2015, 1, 20, 9, 12, 31),
                   'status': QC_STATUS_VALIDATED,
                   'qc_status': 'WARNING',
                   'file_refs': [{'filename': 'jepp',
                                  'filetype': 'holla',
                                  'index': 8,
                                  'status': 'happy',
                                  'submission_id': 'argonaut'}],
                   }

        submission = Submission.from_dict(sm_dict)

        self.assertEqual("3556tr", submission.id)
        self.assertEqual("ttzzrreeww", submission.submission_id)
        self.assertEqual(834569982763, submission.user_id)
        self.assertEqual(datetime(2015, 1, 20, 9, 12, 31), submission.date)
