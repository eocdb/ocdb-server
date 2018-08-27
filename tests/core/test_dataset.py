from unittest import TestCase

from eocdb.core.dataset import Dataset


class DatasetTest(TestCase):
    def test_from_dict(self):
        attribute_names = ['id', 'class']
        records = [
            [1, 'A'],
            [2, 'B'],
            [3, 'C']
        ]
        ds = Dataset.from_dict(dict(records=records, attribute_names=attribute_names))
        self.assertEqual(records, ds.records)
        self.assertEqual(3, ds.record_count)
        self.assertEqual(attribute_names, ds.attribute_names)
        self.assertEqual(2, ds.attribute_count)
