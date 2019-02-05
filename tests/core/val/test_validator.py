from unittest import TestCase

from eocdb.core.models.dataset import Dataset
from eocdb.core.val.validator import Validator


class ValidatorTest(TestCase):

    def setUp(self):
        self._validator = Validator()

    def test_validate_dataset_valid(self):
        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25"}, [], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("OK", result.status)
        self.assertEqual([], result.issues)

    def test_validate_dataset_valid_header_warnings(self):
        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "77.24",
                           "west_longitude": "88.25"}, [], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("WARNING", result.status)
        self.assertEqual(1, len(result.issues))
        self.assertEqual({'description': '@crossing_date_line', 'type': 'WARNING'}, result.issues[0].to_dict())

    def test_validate_dataset_header_error(self):
        dataset = Dataset({"north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25"}, [], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': '@required_field_missing', 'type': 'ERROR'}, result.issues[0].to_dict())
