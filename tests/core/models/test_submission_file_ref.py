from unittest import TestCase

from eocdb.core.models import QC_STATUS_APPROVED, QC_STATUS_PUBLISHED
from eocdb.core.models.submission_file_ref import SubmissionFileRef


class SubmissionFileRefTest(TestCase):

    def test_to_dict(self):
        sfr = SubmissionFileRef(index=12,
                                submission_id="suppe",
                                filename="Margarete",
                                filetype="mixed",
                                status=QC_STATUS_APPROVED)

        self.assertEqual({'filename': 'Margarete',
                          'filetype': 'mixed',
                          'index': 12,
                          'status': QC_STATUS_APPROVED,
                          'submission_id': 'suppe'}, sfr.to_dict())

    def test_from_dict(self):
        sfr_dict={'index': 13, 'submission_id': 'moin!', "filename": "Franz", 'filetype': 'blue', 'status': QC_STATUS_PUBLISHED}

        sfr = SubmissionFileRef.from_dict(sfr_dict)
        self.assertEqual(13, sfr.index)
        self.assertEqual("moin!", sfr.submission_id)
        self.assertEqual("Franz", sfr.filename)
        self.assertEqual("blue", sfr.filetype)
        self.assertEqual(QC_STATUS_PUBLISHED, sfr.status)