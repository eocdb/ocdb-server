from unittest import TestCase

from eocdb.core.models.submission_file_ref import SubmissionFileRef


class SubmissionFileRefTest(TestCase):

    def test_to_dict(self):
        sfr = SubmissionFileRef(index=12,
                                submission_id="suppe",
                                filename="Margarete",
                                status="APPROVED")

        self.assertEqual({'filename': 'Margarete',
                          'index': 12,
                          'status': 'APPROVED',
                          'submission_id': 'suppe'}, sfr.to_dict())

    def test_from_dict(self):
        sfr_dict={'index': 13, 'submission_id': 'moin!', "filename": "Franz", 'status': 'PUBLISHED'}

        sfr = SubmissionFileRef.from_dict(sfr_dict)
        self.assertEqual(13, sfr.index)
        self.assertEqual("moin!", sfr.submission_id)
        self.assertEqual("Franz", sfr.filename)
        self.assertEqual("PUBLISHED", sfr.status)