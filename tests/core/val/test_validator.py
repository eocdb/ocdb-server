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
                           "data_file_name": "the_old_file",
                           "documents": "yes, we have them",
                           "calibration_files": "we have them, too",
                           "data_type": "test data",
                           "water_depth": "80cm",
                           "missing": "where_are_you?",
                           "delimiter": "comma",
                           "fields": "a",
                           "units": "1/m",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_time": "01:12:06[GMT]",
                           "end_time": "02:12:06[GMT]",
                           "start_date": "20110624",
                           "end_date": "20110726"}, [[5], [6]], path="archive/chl01.csv")

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
                           "data_file_name": "the_old_file",
                           "documents": "yes, we have them",
                           "calibration_files": "we have them, too",
                           "data_type": "test data",
                           "water_depth": "80cm",
                           "missing": "where_are_you?",
                           "delimiter": "comma",
                           "fields": "a*ph",
                           "units": "m^2/mg",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "77.24",
                           "west_longitude": "88.25",
                           "start_time": "01:12:06[GMT]",
                           "end_time": "02:12:06[GMT]",
                           "start_date": "20110624",
                           "end_date": "20110726"}, [[7], [8]], path="archive/chl01.csv")

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
                           "data_file_name": "the_old_file",
                           "documents": "yes, we have them",
                           "calibration_files": "we have them, too",
                           "data_type": "test data",
                           "water_depth": "80cm",
                           "missing": "where_are_you?",
                           "delimiter": "comma",
                           "fields": "a*srfa",
                           "units": "m^2/mg",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_time": "01:12:06[GMT]",
                           "end_time": "02:12:06[GMT]",
                           "start_date": "20110624",
                           "end_date": "20110726"
                           }, [[9], [10]], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual(2, len(result.issues))
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': 'The required header field /investigators is not present', 'type': 'ERROR'},
                         result.issues[0].to_dict())
        self.assertEqual({'description': 'The required header field /affiliations is not present', 'type': 'ERROR'},
                         result.issues[1].to_dict())

    def test_validate_dataset_header_enddate_before_startdate(self):
        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "contact": "Dagobert",
                           "experiment": "check WQ",
                           "cruise": "Aida II",
                           "data_file_name": "the_old_file",
                           "documents": "yes, we have them",
                           "calibration_files": "we have them, too",
                           "data_type": "test data",
                           "water_depth": "80cm",
                           "missing": "where_are_you?",
                           "delimiter": "comma",
                           "fields": "aaer",
                           "units": "1/m",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_time": "01:12:06[GMT]",
                           "end_time": "02:12:06[GMT]",
                           "start_date": "20110630",  # <- later than end_date
                           "end_date": "20110626"
                           }, [[11], [12]], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result.issues))
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': 'End date is before start date', 'type': 'ERROR'}, result.issues[0].to_dict())

    def test_validate_dataset_header_experiment_equals_cruise(self):
        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "contact": "Dagobert",
                           "experiment": "Aida II",  # <- are the same but shouldn't
                           "cruise": "Aida II",  # <-
                           "data_file_name": "the_old_file",
                           "documents": "yes, we have them",
                           "calibration_files": "we have them, too",
                           "data_type": "test data",
                           "water_depth": "80cm",
                           "missing": "where_are_you?",
                           "delimiter": "comma",
                           "fields": "abs",
                           "units": "none",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_time": "01:12:06[GMT]",
                           "end_time": "02:12:06[GMT]",
                           "start_date": "20110630",
                           "end_date": "20110726"
                           }, [[13], [14]], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result.issues))
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': "Header /cruise should not be the same as /experiment, please "
                                         "make /cruise a 'subset' of /experiment.", 'type': 'ERROR'},
                         result.issues[0].to_dict())

    def test_validate_dataset_obsolete_field(self):
        metadata = {'delimiter': 'comma'}

        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "contact": "Dagobert",
                           "experiment": "check WQ",
                           "cruise": "Aida II",
                           "data_file_name": "the_old_file",
                           "documents": "yes, we have them",
                           "calibration_files": "we have them, too",
                           "station_alt_id": "we do not care about this value",  # <- triggers the warning
                           "data_type": "test data",
                           "water_depth": "80cm",
                           "missing": "where_are_you?",
                           "delimiter": "comma",
                           "fields": "abs_blank_ap",
                           "units": "none",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_time": "01:12:06[GMT]",
                           "end_time": "02:12:06[GMT]",
                           "start_date": "20110624",
                           "end_date": "20110726"}, [[13], [14]], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result.issues))
        self.assertEqual("WARNING", result.status)
        self.assertEqual({'description': "The header field /station_alt_id is marked as obsolete, "
                                         "please check the documentation.", 'type': 'WARNING'},
                         result.issues[0].to_dict())

    def test_validate_dataset_field_units_mismatch(self):
        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "contact": "Dagobert",
                           "experiment": "check WQ",
                           "cruise": "Aida II",
                           "data_file_name": "the_old_file",
                           "documents": "yes, we have them",
                           "calibration_files": "we have them, too",
                           "data_type": "test data",
                           "water_depth": "80cm",
                           "missing": "where_are_you?",
                           "delimiter": "comma",
                           "fields": "a,b",
                           "units": "1/m",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_time": "01:12:06[GMT]",
                           "end_time": "02:12:06[GMT]",
                           "start_date": "20110624",
                           "end_date": "20110726"}, [[5], [6]], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': 'Number of fields and units does not match. Skipping parsing '
                                         'of measurement records.',
                          'type': 'ERROR'}, result.issues[0].to_dict())

    def test_validate_dataset_unlisted_variable(self):
        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "contact": "Dagobert",
                           "experiment": "check WQ",
                           "cruise": "Aida II",
                           "data_file_name": "the_old_file",
                           "documents": "yes, we have them",
                           "calibration_files": "we have them, too",
                           "data_type": "test data",
                           "water_depth": "80cm",
                           "missing": "where_are_you?",
                           "delimiter": "comma",
                           "fields": "heffalump",
                           "units": "1/m",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_time": "01:12:06[GMT]",
                           "end_time": "02:12:06[GMT]",
                           "start_date": "20110624",
                           "end_date": "20110726"}, [[5], [6]], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("WARNING", result.status)
        self.assertEqual(1, len(result.issues))
        self.assertEqual({'description': 'Variable not listed in valid variables: heffalump',
                          'type': 'WARNING'}, result.issues[0].to_dict())

    def test_validate_dataset_value_below_lower_bound(self):
        dataset = Dataset({"investigators": "Daniel_Duesentrieb",
                           "affiliations": "Entenhausen",
                           "contact": "Dagobert",
                           "experiment": "check WQ",
                           "cruise": "Aida II",
                           "data_file_name": "the_old_file",
                           "documents": "yes, we have them",
                           "calibration_files": "we have them, too",
                           "data_type": "test data",
                           "water_depth": "80cm",
                           "missing": "where_are_you?",
                           "delimiter": "comma",
                           "fields": "abs_blank_ag,abs*,abs_ad",
                           "units": "none,m^2/mg,none",
                           "north_latitude": "37.34",
                           "south_latitude": "34.96",
                           "east_longitude": "108.24",
                           "west_longitude": "88.25",
                           "start_time": "01:12:06[GMT]",
                           "end_time": "02:12:06[GMT]",
                           "start_date": "20110624",
                           "end_date": "20110726"},
                          [[5.0, 6.1, 7.2],
                           [6.1, 7.2, 8.3],
                           [6.2, -1.0, 8.4]], path="archive/chl01.csv")

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("ERROR", result.status)
        self.assertEqual(1, len(result.issues))
        self.assertEqual({'description': "Measurement #3: The 'abs*' field has value (-1.0) outside "
                                         'expected range [0.0 - nan].',
                          'type': 'ERROR'}, result.issues[0].to_dict())

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
