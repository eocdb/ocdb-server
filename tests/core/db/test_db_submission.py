from datetime import datetime
from unittest import TestCase

from eocdb.core.db.db_submission import DbSubmission
from eocdb.core.models import DatasetValidationResult, Issue
from eocdb.core.models.submission_file import SubmissionFile


class DbSubmissionTest(TestCase):

    def test_to_dict(self):
        files = [SubmissionFile(submission_id="submitme",
                                index=0, filename="Hans",
                                status="SUBMITTED",
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id="submitme",
                                index=1, filename="Helga",
                                status="VALIDATED",
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]
        subm = DbSubmission(status="Hellyeah", user_id=88763, submission_id="submitme", files=files,
                            date=datetime(2001, 2, 3, 4, 5, 6))

        self.assertEqual({'date': datetime(2001, 2, 3, 4, 5, 6),
                          'file_refs': [],
                          'files': [{'filename': 'Hans',
                                     'index': 0,
                                     'result': {'issues': [], 'status': 'OK'},
                                     'status': 'SUBMITTED',
                                     'submission_id': 'submitme'},
                                    {'filename': 'Helga',
                                     'index': 1,
                                     'result': {'issues': [{'description': 'This might be wrong',
                                                            'type': 'WARNING'}],
                                                'status': 'WARNING'},
                                     'status': 'VALIDATED',
                                     'submission_id': 'submitme'}],
                          'id': None,
                          'status': 'Hellyeah',
                          'submission_id': 'submitme',
                          'user_id': 88763}, subm.to_dict())

    def test_from_dict(self):
        subm_dict = {'date': datetime(2002, 3, 4, 5, 6, 7),
         'file_refs': [],
         'files': [{'filename': 'Werner',
                    'index': 0,
                    'result': {'issues': [], 'status': 'OK'},
                    'status': 'SUBMITTED',
                    'submission_id': 'submitme'},
                   {'filename': 'Warburga',
                    'index': 1,
                    'result': {'issues': [{'description': 'This might be wrong',
                                           'type': 'WARNING'}],
                               'status': 'WARNING'},
                    'status': 'VALIDATED',
                    'submission_id': 'submitme'}],
         'id': None,
         'status': 'Yo!',
         'submission_id': 'submitme',
         'user_id': 88764}

        subm = DbSubmission.from_dict(subm_dict)
        self.assertEqual(datetime(2002, 3, 4, 5, 6, 7), subm.date)
        self.assertEqual(2, len(subm.files))
        self.assertEqual("Werner", subm.files[0]["filename"])
        self.assertEqual(0, subm.files[0]["index"])

    def test_to_submission(self):
        files = [SubmissionFile(submission_id="submitme",
                                index=0, filename="Hans",
                                status="SUBMITTED",
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id="submitme",
                                index=1, filename="Helga",
                                status="VALIDATED",
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]
        db_subm = DbSubmission(status="Hellyeah", user_id=88763, submission_id="submitme", files=files,
                            date=datetime(2001, 2, 3, 4, 5, 6))

        subm = db_subm.to_submission()

        self.assertEqual(datetime(2001, 2, 3, 4, 5, 6), subm.date)
        self.assertEqual(2, len(subm.file_refs))
        self.assertEqual("Hans", subm.file_refs[0].filename)
        self.assertEqual(0, subm.file_refs[0].index)





