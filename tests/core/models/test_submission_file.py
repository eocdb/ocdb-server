from unittest import TestCase

from eocdb.core.models import DatasetValidationResult, Issue, QC_STATUS_SUBMITTED, QC_STATUS_VALIDATED
from eocdb.core.models.submission_file import SubmissionFile


class SubmissionFileTest(TestCase):

    def test_to_dict(self):
        dsvr = DatasetValidationResult(status="OK", issues=[])
        sf = SubmissionFile(index=11,
                            submission_id="yeswecan",
                            filename="is_a_secret",
                            filetype="DOC",
                            status=QC_STATUS_SUBMITTED,
                            result=dsvr)

        sf_dict = sf.to_dict()
        self.assertEqual({'filename': 'is_a_secret',
                          'filetype': 'DOC',
                          'index': 11,
                          'result': {'issues': [], 'status': 'OK'},
                          'status': QC_STATUS_SUBMITTED,
                          'submission_id': 'yeswecan'}, sf_dict)

    def test_from_dict(self):
        sf_dict = {'index': 12, 'submission_id': 'whatthehell', 'filename': 'file_in_c_sharp',
                   'filetype': 'MEASUREMENT', 'result': {'issues': [], 'status': 'OK'}, 'status': QC_STATUS_VALIDATED}

        sf = SubmissionFile.from_dict(sf_dict)
        self.assertEqual(12, sf.index)
        self.assertEqual('whatthehell', sf.submission_id)
        self.assertEqual('file_in_c_sharp', sf.filename)
        self.assertEqual('MEASUREMENT', sf.filetype)
        self.assertEqual("OK", sf.result["status"])
        self.assertEqual(QC_STATUS_VALIDATED, sf.status)

    def test_to_ref(self):
        dsvr = DatasetValidationResult(status="ERROR", issues=[Issue(type="ERROR", description="Yo, not like that my son")])
        sf = SubmissionFile(index=11,
                            submission_id="yeswecan",
                            filename="is_a_secret",
                            filetype="a cool one",
                            status=QC_STATUS_SUBMITTED,
                            result=dsvr)

        sfr = sf.to_ref()
        self.assertEqual(11, sfr.index)
        self.assertEqual("yeswecan", sfr.submission_id)
        self.assertEqual("is_a_secret", sfr.filename)
        self.assertEqual("a cool one", sfr.filetype)
        self.assertEqual(QC_STATUS_SUBMITTED, sfr.status)
