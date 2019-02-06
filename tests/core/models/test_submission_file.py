from unittest import TestCase

from eocdb.core.models import DatasetValidationResult
from eocdb.core.models.submission_file import SubmissionFile


class SubmissionFileTest(TestCase):

    def test_to_dict(self):
        dsvr = DatasetValidationResult(status="OK", issues=[])
        sf = SubmissionFile(index=11,
                            submission_id="yeswecan",
                            filename="is_a_secret",
                            status="SUBMITTED",
                            result=dsvr)

        sf_dict = sf.to_dict()
        self.assertEqual({'filename': 'is_a_secret',
                          'index': 11,
                          'result': {'issues': [], 'status': 'OK'},
                          'status': 'SUBMITTED',
                          'submission_id': 'yeswecan'}, sf_dict)

    def test_from_dict(self):
        sf_dict = {'index': 12, 'submission_id': 'whatthehell', 'filename': 'file_in_c_sharp', 'result': {'issues': [], 'status': 'OK'}, 'status': 'VALIDATED'}

        sf = SubmissionFile.from_dict(sf_dict)
        self.assertEqual(12, sf.index)
        self.assertEqual('whatthehell', sf.submission_id)
        self.assertEqual('file_in_c_sharp', sf.filename)
        self.assertEqual("OK", sf.result["status"])
        self.assertEqual("VALIDATED", sf.status)
