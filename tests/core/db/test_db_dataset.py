import datetime
from unittest import TestCase

from tests.helpers import new_test_db_dataset


class DbDatsetTest(TestCase):

    def setUp(self):
        self.dataset = new_test_db_dataset(3)
        self.dataset._records = []
        self.dataset._metadata = {}

    def test_add_records_and_get(self):
        record_1 = [-38.4, 109.8, 0.266612499]
        record_2 = [-38.5, 109.9, 0.366612499]

        self.dataset.add_record(record_1)
        self.assertEqual(1, self.dataset.record_count)

        self.dataset.add_record(record_2)
        self.assertEqual(2, self.dataset.record_count)

        records = self.dataset.records
        self.assertAlmostEqual(-38.4, records[0][0], 8)
        self.assertAlmostEqual(109.9, records[1][1], 8)

    def test_to_dict_empty(self):
        self.assertEqual({'attributes': [],
                          'groups': [],
                          'latitudes': [],
                          'longitudes': [],
                          'id': None,
                          'metadata': {},
                          'records': [],
                          'path': 'archive',
                          'filename': 'dataset-3.txt',
                          'user_id': '1',
                          'submission_id': 'abc',
                          'status': 'PUBLISHED',  # comes from test-dataset
                          'times': []}, self.dataset.to_dict())

    def test_to_dict(self):
        record_1 = [-39.4, 110.8, 0.267612499]
        record_2 = [-39.5, 110.9, 0.367612499]
        groups = ["Chl"]

        self.dataset.add_metadatum("key_1", "value_1")
        self.dataset.add_metadatum("key_2", "value_2")
        self.dataset.add_attributes(['lat', 'lon', 'chl'])
        self.dataset.groups = groups
        self.dataset.add_geo_location(-107.23, 18.076)
        self.dataset.add_time(datetime.datetime(2008, 10, 4, 15, 22, 51))
        self.dataset.add_record(record_1)
        self.dataset.add_record(record_2)

        self.assertEqual({'attributes': ['lat', 'lon', 'chl'],
                          'groups': ['Chl'],
                          'latitudes': [18.076],
                          'longitudes': [-107.23],
                          'id': None,
                          'metadata': {'key_1': 'value_1', 'key_2': 'value_2'},
                          'records': [[-39.4, 110.8, 0.267612499], [-39.5, 110.9, 0.367612499]],
                          'path': 'archive',
                          'filename': 'dataset-3.txt',
                          'user_id': '1',
                          'submission_id': 'abc',
                          'status': 'PUBLISHED',
                          'times': ['2008-10-04T15:22:51']},
                         self.dataset.to_dict())

    def test_add_attributes_and_get(self):
        attribute_names = ["lon", "lat", "chl"]

        self.dataset.add_attributes(attribute_names)

        self.assertEqual(3, self.dataset.attribute_count)
        self.assertEqual(attribute_names, self.dataset.attribute_names)

    def test_add_metadatum_and_get(self):
        self.assertEqual(0, len(self.dataset.metadata))

        self.dataset.add_metadatum("key_1", "value_1")
        self.assertEqual(1, len(self.dataset.metadata))

        self.dataset.add_metadatum("key_2", "value_2")
        self.assertEqual(2, len(self.dataset.metadata))

        self.assertEqual("value_2", self.dataset.metadata["key_2"])

    def test_add_geo_location_and_get(self):
        self.assertEqual(0, len(self.dataset.longitudes))
        self.assertEqual(0, len(self.dataset.latitudes))

        self.dataset.add_geo_location(12, 13)
        self.dataset.add_geo_location(14, 15)

        self.assertEqual(2, len(self.dataset.longitudes))
        self.assertAlmostEqual(12.0, self.dataset.longitudes[0], 8)
        self.assertAlmostEqual(14.0, self.dataset.longitudes[1], 8)

        self.assertEqual(2, len(self.dataset.latitudes))
        self.assertAlmostEqual(13.0, self.dataset.latitudes[0], 8)
        self.assertAlmostEqual(15.0, self.dataset.latitudes[1], 8)

    def test_add_times_and_get(self):
        self.assertEqual(0, len(self.dataset.times))

        self.dataset.add_time(datetime.datetime.utcnow())
        self.dataset.add_time(datetime.datetime.utcnow())

        self.assertEqual(2, len(self.dataset.times))
