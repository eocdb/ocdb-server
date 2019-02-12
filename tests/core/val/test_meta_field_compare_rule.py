import unittest
from datetime import datetime

from eocdb.core.models import Dataset, ISSUE_TYPE_ERROR, ISSUE_TYPE_WARNING
from eocdb.core.val._meta_field_compare_rule import MetaFieldCompareRule
from tests.core.val._mock_library import MockLibrary


class MetaFieldCompareRuleTest(unittest.TestCase):

    def setUp(self):
        self._lib = MockLibrary()

    def test_float_larger_equal_success(self):
        rule = MetaFieldCompareRule("north_lat", "south_lat", ">=", error="@south_north_mismatch", data_type="number")

        dataset = Dataset({"north_lat": "34.56", "south_lat": "28.33"}, [])

        self.assertIsNone(rule.eval(dataset, self._lib))

    def test_float_larger_equal_error(self):
        rule = MetaFieldCompareRule("north_lat", "south_lat", ">=", error="@south_north_mismatch", data_type="number")

        dataset = Dataset({"north_lat": "11.56", "south_lat": "28.33"}, [])

        issue = rule.eval(dataset, self._lib)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_ERROR, issue.type)
        self.assertEqual("@south_north_mismatch", issue.description)

    def test_float_not_equal_warning(self):
        rule = MetaFieldCompareRule("north_lat", "south_lat", "!=", warning="should not be equal", data_type="number")

        dataset = Dataset({"north_lat": "28.33", "south_lat": "28.33"}, [])

        issue = rule.eval(dataset, self._lib)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_WARNING, issue.type)
        self.assertEqual("should not be equal", issue.description)

    def test_int_less_than_error(self):
        rule = MetaFieldCompareRule("int_1", "int_2", "<", warning="should be smaller", data_type="number")

        dataset = Dataset({"int_1": "16", "int_2": "15"}, [])

        issue = rule.eval(dataset, self._lib)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_WARNING, issue.type)
        self.assertEqual("should be smaller", issue.description)

    def test_int_equal_invalid_field(self):
        rule = MetaFieldCompareRule("int_1", "int_2", "==", error="must be same", data_type="number")

        dataset = Dataset({"int_1": "16"}, [])

        issue = rule.eval(dataset, self._lib)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_ERROR, issue.type)
        self.assertEqual("Requested field not contained in metadata: int_2", issue.description)

    def test_date_smaller_equal_success(self):
        rule = MetaFieldCompareRule("start_date", "end_date", "<=", error="end date before start date", data_type="date")

        dataset = Dataset({"start_date": "20080416", "end_date": "20080416"}, [])

        self.assertIsNone(rule.eval(dataset, self._lib))

    def test_date_smaller_equal_failure(self):
        rule = MetaFieldCompareRule("start_date", "end_date", "<", error="end date before start date", data_type="date")

        dataset = Dataset({"start_date": "20080416", "end_date": "20080416"}, [])

        issue = rule.eval(dataset, self._lib)
        self.assertIsNotNone(issue)
        self.assertEqual("end date before start date", issue.description)
        self.assertEqual("ERROR", issue.type)

    def test_extract_value_not_present(self):
        metadata = {"bla": "whocares"}

        rule = MetaFieldCompareRule("north_lat", "south_lat", ">=", error="@south_north_mismatch", data_type="number")

        self.assertIsNone(rule._extract_value("north_lat", metadata))

    def test_extract_value_number(self):
        metadata = {"south_lat": "67.555"}

        rule = MetaFieldCompareRule("north_lat", "south_lat", ">=", error="@south_north_mismatch", data_type="number")

        self.assertEqual(67.555, rule._extract_value("south_lat", metadata))

    def test_extract_value_number_with_unit(self):
        metadata = {"south_lat": "68.666[DEG]"}

        rule = MetaFieldCompareRule("north_lat", "south_lat", ">=", error="@south_north_mismatch", data_type="number")

        self.assertEqual(68.666, rule._extract_value("south_lat", metadata))

    def test_extract_value_date(self):
        metadata = {"start_date": "20121113"}

        rule = MetaFieldCompareRule("end_date", "start_date", ">=", error="@whatever", data_type="date")

        self.assertEqual(datetime(2012, 11, 13), rule._extract_value("start_date", metadata))

    def test_convert_date_string(self):
        self.assertEqual("2008-09-23", MetaFieldCompareRule._convert_date_string("20080923"))
