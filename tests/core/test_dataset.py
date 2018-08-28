from unittest import TestCase

from eocdb.core.dataset import Dataset


class DatasetTest(TestCase):
    def test_from_dict(self):
        metadata = {"temperature": 269.2}
        attribute_names = ['id', 'class']
        records = [
            [1, 'A'],
            [2, 'B'],
            [3, 'C']
        ]
        ds = Dataset.from_dict(dict(metadata=metadata, records=records, attribute_names=attribute_names))
        self.assertEqual(metadata, ds.metadata)
        self.assertEqual(records, ds.records)
        self.assertEqual(3, ds.record_count)
        self.assertEqual(attribute_names, ds.attribute_names)
        self.assertEqual(2, ds.attribute_count)

    def test_from_dict_empty(self):
        ds = Dataset.from_dict(dict())
        self.assertEqual({}, ds.metadata)
        self.assertEqual([], ds.records)
        self.assertEqual(0, ds.record_count)
        self.assertEqual([], ds.attribute_names)
        self.assertEqual(0, ds.attribute_count)
