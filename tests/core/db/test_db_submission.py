from datetime import datetime
from unittest import TestCase

from eocdb.core.db.db_submission import DbSubmission
from eocdb.core.models import DatasetValidationResult, Issue, QC_STATUS_SUBMITTED, QC_STATUS_VALIDATED
from eocdb.core.models.submission_file import SubmissionFile


class DbSubmissionTest(TestCase):

    def test_to_dict(self):
        files = [SubmissionFile(submission_id="submitme",
                                index=0,
                                filename="Hans",
                                filetype="DOC",
                                status=QC_STATUS_SUBMITTED,
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id="submitme",
                                index=1,
                                filename="Helga",
                                filetype="MEAS",
                                status=QC_STATUS_VALIDATED,
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]
        subm = DbSubmission(status="Hellyeah", user_id=88763, submission_id="submitme", path="/the/archive/root/",
                            files=files, qc_status="warning", date=datetime(2001, 2, 3, 4, 5, 6),
                            publication_date=datetime(2002, 2, 3, 4, 5, 6),
                            allow_publication=True)

        self.assertEqual({'date': datetime(2001, 2, 3, 4, 5, 6),
                          'file_refs': [],
                          'files': [{'filename': 'Hans',
                                     'filetype': 'DOC',
                                     'index': 0,
                                     'result': {'issues': [], 'status': 'OK'},
                                     'status': QC_STATUS_SUBMITTED,
                                     'submission_id': 'submitme'},
                                    {'filename': 'Helga',
                                     'filetype': 'MEAS',
                                     'index': 1,
                                     'result': {'issues': [{'description': 'This might be wrong',
                                                            'type': 'WARNING'}],
                                                'status': 'WARNING'},
                                     'status': QC_STATUS_VALIDATED,
                                     'submission_id': 'submitme'}],
                          'id': None,
                          'path': '/the/archive/root/',
                          'publication_date': datetime(2002, 2, 3, 4, 5, 6),
                          'allow_publication': True,
                          'qc_status': 'warning',
                          'status': 'Hellyeah',
                          'submission_id': 'submitme',
                          'user_id': 88763}, subm.to_dict())

    def test_from_dict(self):
        subm_dict = {'date': datetime(2002, 3, 4, 5, 6, 7),
                     'file_refs': [],
                     'files': [{'filename': 'Werner',
                                'index': 0,
                                'result': {'issues': [], 'status': 'OK'},
                                'status': QC_STATUS_SUBMITTED,
                                'submission_id': 'submitme'},
                               {'filename': 'Warburga',
                                'index': 1,
                                'result': {'issues': [{'description': 'This might be wrong',
                                                       'type': 'WARNING'}],
                                           'status': 'WARNING'},
                                'status': QC_STATUS_VALIDATED,
                                'submission_id': 'submitme'}],
                     'id': None,
                     'status': 'Yo!',
                     'qc_status': 'Very good',
                     'submission_id': 'submitme',
                     'path': 'up where we belong',
                     'publication_date': datetime(2002, 2, 3, 4, 5, 6),
                     'allow_publication': True,
                     'user_id': 88764}

        subm = DbSubmission.from_dict(subm_dict)
        self.assertEqual(datetime(2002, 3, 4, 5, 6, 7), subm.date)
        self.assertEqual(2, len(subm.files))
        self.assertEqual("Werner", subm.files[0].filename)
        self.assertEqual(0, subm.files[0].index)
        self.assertEqual("Warburga", subm.files[1].filename)
        self.assertEqual(1, subm.files[1].index)

    def test_to_submission(self):
        files = [SubmissionFile(submission_id="submitme",
                                index=0,
                                filename="Hans",
                                filetype="black",
                                status=QC_STATUS_SUBMITTED,
                                result=DatasetValidationResult(status="OK", issues=[])),
                 SubmissionFile(submission_id="submitme",
                                index=1,
                                filename="Helga",
                                filetype="green",
                                status=QC_STATUS_VALIDATED,
                                result=DatasetValidationResult(status="WARNING", issues=[
                                    Issue(type="WARNING", description="This might be wrong")]))]
        db_subm = DbSubmission(status="Hellyeah", user_id=88763, submission_id="submitme", files=files, qc_status="OK",
                               path="/root/hell/yeah", date=datetime(2001, 2, 3, 4, 5, 6))

        subm = db_subm.to_submission()

        self.assertEqual(datetime(2001, 2, 3, 4, 5, 6), subm.date)
        self.assertEqual(2, len(subm.file_refs))
        self.assertEqual("Hans", subm.file_refs[0].filename)
        self.assertEqual(0, subm.file_refs[0].index)
