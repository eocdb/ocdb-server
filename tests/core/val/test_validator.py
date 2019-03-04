from unittest import TestCase

from eocdb.core.models.dataset import Dataset
from eocdb.core.seabass.sb_file_reader import SbFileReader
from eocdb.core.val._gap_aware_dict import GapAwareDict
from eocdb.core.val.validator import Validator


class ValidatorTest(TestCase):

    def setUp(self):
        self._validator = Validator()

    def test_validate_dataset_valid(self):
        dataset = self._create_valid_dataset()

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("OK", result.status)
        self.assertEqual([], result.issues)

    def test_validate_dataset_dateline_warning(self):
        dataset = self._create_valid_dataset()

        dataset.metadata["east_longitude"] = "77.24"
        dataset.metadata["west_longitude"] = "88.25"

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("WARNING", result.status)
        self.assertEqual(1, len(result.issues))
        self.assertEqual({'description': '/east_longitude [77.24] < west_longitude [88.25], implies '
                                         'crossing the dateline! If you did not do so, please check '
                                         'these values', 'type': 'WARNING'}, result.issues[0].to_dict())

    def test_validate_dataset_header_error(self):
        dataset = self._create_valid_dataset()

        del dataset.metadata["investigators"]
        del dataset.metadata["affiliations"]

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual(2, len(result.issues))
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': 'The required header field /investigators is not present', 'type': 'ERROR'},
                         result.issues[0].to_dict())
        self.assertEqual({'description': 'The required header field /affiliations is not present', 'type': 'ERROR'},
                         result.issues[1].to_dict())

    def test_validate_dataset_header_enddate_before_startdate(self):
        dataset = self._create_valid_dataset()

        dataset.metadata["start_date"] = "20110630"  # <- later than end_date
        dataset.metadata["end_date"] = "20110626"

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result.issues))
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': 'Header error: start date/time (2011-06-30 00:00:00) must '
                                         + 'occur before end date/time (2011-06-26 00:00:00)', 'type': 'ERROR'},
                         result.issues[0].to_dict())

    def test_validate_dataset_header_experiment_equals_cruise(self):
        dataset = self._create_valid_dataset()

        dataset.metadata["experiment"] = "Aida II"
        dataset.metadata["cruise"] = "Aida II"

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result.issues))
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': "Header /cruise should not be the same as /experiment, please "
                                         "make /cruise a 'subset' of /experiment.", 'type': 'ERROR'},
                         result.issues[0].to_dict())

    def test_validate_dataset_obsolete_field(self):
        dataset = self._create_valid_dataset()

        dataset.metadata["station_alt_id"] = "we do not care about this value"

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result.issues))
        self.assertEqual("WARNING", result.status)
        self.assertEqual({'description': "The header field /station_alt_id is marked as obsolete, "
                                         "please check the documentation.", 'type': 'WARNING'},
                         result.issues[0].to_dict())

    def test_validate_dataset_field_units_mismatch(self):
        dataset = self._create_valid_dataset()

        dataset.metadata["fields"] = "a,b"
        dataset.metadata["units"] = "1/m"

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': 'Number of fields and units does not match. Skipping parsing '
                                         'of measurement records.',
                          'type': 'ERROR'}, result.issues[0].to_dict())

    def test_validate_dataset_field_missing(self):
        dataset = self._create_valid_dataset()

        del dataset.metadata["fields"]

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual(2, len(result.issues))
        self.assertEqual("ERROR", result.status)
        self.assertEqual({'description': 'The required header field /fields is not present',
                          'type': 'ERROR'}, result.issues[0].to_dict())
        self.assertEqual({'description': 'Header tags /fields or /units missing. Skipping parsing of '
                                         'measurement records.',
                          'type': 'ERROR'}, result.issues[1].to_dict())

    def test_validate_dataset_unlisted_variable(self):
        dataset = self._create_valid_dataset()

        dataset.metadata["fields"] = "heffalump"
        dataset.metadata["units"] = "1/m"

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("WARNING", result.status)
        self.assertEqual(1, len(result.issues))
        self.assertEqual({'description': 'Variable not listed in valid variables: heffalump',
                          'type': 'WARNING'}, result.issues[0].to_dict())

    def test_validate_dataset_value_below_lower_bound(self):
        dataset = self._create_valid_dataset()

        dataset.metadata["fields"] = "abs_blank_ag,abs*,abs_ad"
        dataset.metadata["units"] = "none,m^2/mg,none"
        dataset.records = [[5.0, 6.1, 7.2],
                           [6.1, 7.2, 8.3],
                           [6.2, -1.0, 8.4]]

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("ERROR", result.status)
        self.assertEqual(1, len(result.issues))
        self.assertEqual({'description': "Measurement #3: The 'abs*' field has value (-1.0) outside "
                                         'expected range [0.0 - inf].',
                          'type': 'ERROR'}, result.issues[0].to_dict())

    def test_validate_dataset_float_and_string_error_empty_string(self):
        dataset = self._create_valid_dataset()

        dataset.metadata["fields"] = "aph,associated_files,ap_unc"
        dataset.metadata["units"] = "1/m,none,1/m"
        dataset.records = [[5.0, "willi", 7.2],
                           [6.1, "", 8.3],
                           [6.2, "ottilie", 8.4]]

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("ERROR", result.status)
        self.assertEqual(1, len(result.issues))
        self.assertEqual({'description': "Measurement #2: The value for 'associated_files' is empty.",
                          'type': 'ERROR'}, result.issues[0].to_dict())

    def test_validate_dataset_float_and_date_error_invalid_month(self):
        dataset = self._create_valid_dataset()

        dataset.metadata["fields"] = "cond,cloud,date"
        dataset.metadata["units"] = "mmho/cm,%,none"
        dataset.records = [[5.0, 12.8, "20011103"],
                           [6.1, 13.7, "20021204"],
                           [6.2, 15.2, "20030016"]]

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("ERROR", result.status)
        self.assertEqual(1, len(result.issues))
        self.assertEqual({'description': "Measurement #3: The value for 'date' is malformed (invalid "
                                         "month detected)",
                          'type': 'ERROR'}, result.issues[0].to_dict())

    def test_validate_dataset_float_with_missing_value(self):
        dataset = self._create_valid_dataset()

        dataset.metadata["missing"] = -117
        dataset.metadata["fields"] = "abs_blank_ag,abs*,abs_ad"
        dataset.metadata["units"] = "none,m^2/mg,none"
        dataset.records = [[5.0, 6.1, 7.2],
                           [-117, 7.2, 8.3],
                           [6.2, -117, 8.4]]

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("OK", result.status)

    def test_validate_dataset_float_with_wavelength_in_varname(self):
        dataset = self._create_valid_dataset()

        dataset.metadata["missing"] = -117
        dataset.metadata["fields"] = "depth,bw529,bw657"
        dataset.metadata["units"] = "m,1/m,1/m"
        dataset.records = [[3.068489, 0.003527, 0.001992],
                           [4.076861, 0.003527, 0.001992],
                           [5.047225, 0.003527, 0.001992]]

        result = self._validator.validate_dataset(dataset)
        self.assertIsNotNone(result)
        self.assertEqual("OK", result.status)

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

    def test_strip_wavelength_no_wavelength(self):
        stripped = self._validator._strip_wavelength("absozytes")
        self.assertEqual("absozytes", stripped)

    def test_strip_wavelength(self):
        stripped = self._validator._strip_wavelength("bzgd669")
        self.assertEqual("bzgd", stripped)

    @staticmethod
    def _create_valid_dataset():
        return Dataset({"investigators": "Daniel_Duesentrieb",
                        "affiliations": "Entenhausen",
                        "contact": "Dagobert",
                        "experiment": "check WQ",
                        "cruise": "Aida II",
                        "data_file_name": "the_old_file",
                        "documents": "yes, we have them",
                        "calibration_files": "we have them, too",
                        "data_type": "test data",
                        "water_depth": "80cm",
                        "missing": "-999.0",
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

    # def test_delete_me(self):
    #     reader = SbFileReader()
    #     data_record = reader.read("/usr/local/data/OC_DB/seabass_extract/USF/HU/Tampa_Bay/t1205/archive/T12050705_rrs.txt")
    #     result = self._validator.validate_dataset(data_record)
    #     print(result)
