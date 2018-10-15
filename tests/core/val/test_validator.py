from unittest import TestCase

from eocdb.core.models.bucket import Bucket
from eocdb.core.models.dataset import Dataset
from eocdb.core.models.issue import Issue
from eocdb.core.val.validator import validate_dataset


class ValidatorTest(TestCase):

    def test_validate_dataset(self):
        dataset = Dataset(Bucket("a", "p", "c"), "ds", "new", {}, [], id_=None)
        result = validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("OK", result.status)
        self.assertEqual([], result.issues)

        dataset.id = "x"
        result = validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("WARNING", result.status)
        issue = Issue("WARNING", "Datasets should have no ID before insert or update")
        self.assertEqual([issue], result.issues)
