from unittest import TestCase

from eocdb.core.models.dataset import Dataset
from eocdb.core.val._gap_aware_dict import GapAwareDict
from eocdb.core.val.validator import Validator


class ValidatorTest(TestCase):

    def setUp(self):
        self._validator = Validator()

    def test_validate_dataset_valid(self):
        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "contact": "Dagobert",
                           "experiment": "check WQ",
                           "cruise": "Aida II",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_date": "20110624",
                           "end_date": "20110726"}, [], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("OK", result.status)
        self.assertEqual([], result.issues)

    def test_validate_dataset_valid_header_warnings(self):
        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "contact": "Dagobert",
                           "experiment": "check WQ",
                           "cruise": "Aida II",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "77.24",
                           "west_longitude": "88.25",
                           "start_date": "20110624",
                           "end_date": "20110726"}, [], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("WARNING", result.status)
        self.assertEqual(1, len(result.issues))
        self.assertEqual({'description': '/east_longitude [77.24] < west_longitude [88.25], implies '
                                         'crossing the dateline! If you did not do so, please check '
                                         'these values', 'type': 'WARNING'}, result.issues[0].to_dict())

    def test_validate_dataset_header_error(self):
        dataset = Dataset({"experiment": "check WQ",
                           "contact": "Dagobert",
                           "cruise": "Aida II",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_date": "20110624",
                           "end_date": "20110726"
                           }, [], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': 'The required header field /investigators is not present', 'type': 'ERROR'},
                         result.issues[0].to_dict())

    def test_validate_dataset_header_enddate_before_startdate(self):
        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "contact": "Dagobert",
                           "experiment": "check WQ",
                           "cruise": "Aida II",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_date": "20110630",
                           "end_date": "20110626"
                           }, [], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': 'End date is before start date', 'type': 'ERROR'}, result.issues[0].to_dict())

    def test_validate_dataset_header_experiment_equals_cruise(self):
        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "contact": "Dagobert",
                           "experiment": "Aida II",
                           "cruise": "Aida II",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_date": "20110630",
                           "end_date": "20110726"
                           }, [], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': "Header /cruise should not be the same as /experiment, please "
                                         "make /cruise a 'subset' of /experiment.", 'type': 'ERROR'},
                         result.issues[0].to_dict())

    def test_validate_dataset_obsolete_field(self):
        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "contact": "Dagobert",
                           "experiment": "check WQ",
                           "cruise": "Aida II",
                           "station_alt_id": "we do not care about this value",  # <- triggers the warning
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_date": "20110624",
                           "end_date": "20110726"}, [], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("WARNING", result.status)
        self.assertEqual({'description': "The header field /station_alt_id is marked as obsolete, "
                                         "please check the documentation.", 'type': 'WARNING'},
                         result.issues[0].to_dict())

    def test_resolve_warning_clear_message(self):
        dict = GapAwareDict({"reference": "reffi",
                             "compare": "compi",
                             "ref_val": "127",
                             "comp_val": "128"})
        self.assertEqual("Header field /reffi is below 128",
                         self._validator.resolve_warning("Header field /{reference} is below {comp_val}", dict))

    def test_resolve_warning_library_message(self):
        dict = GapAwareDict({"reference": "reffi",
                             "compare": "compi",
                             "ref_val": "127",
                             "comp_val": "128"})
        self.assertEqual("The value of the header field /reffi is missing",
                         self._validator.resolve_warning("@field_value_missing", dict))

    def test_resolve_error_clear_message(self):
        dict = GapAwareDict({"reference": "reffi",
                             "compare": "compi",
                             "ref_val": "127",
                             "comp_val": "128"})
        self.assertEqual("Header field /reffi should be equal to '128' but is '127'",
                         self._validator.resolve_error(
                             "Header field /{reference} should be equal to '{comp_val}' but is '{ref_val}'", dict))

    def test_resolve_error_library_message(self):
        dict = GapAwareDict({"reference": "reffi",
                             "compare": "compi",
                             "ref_val": "127",
                             "comp_val": "128"})
        self.assertEqual("The required header field /reffi is not present",
                         self._validator.resolve_error("@required_field_missing", dict))
