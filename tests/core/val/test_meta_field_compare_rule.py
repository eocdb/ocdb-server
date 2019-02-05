import unittest

from eocdb.core.models import Dataset, ISSUE_TYPE_ERROR, ISSUE_TYPE_WARNING
from eocdb.core.val._meta_field_compare_rule import MetaFieldCompareRule


class MetaFieldCompareRuleTest(unittest.TestCase):

    def test_float_larger_equal_success(self):
        rule = MetaFieldCompareRule("north_lat", "south_lat", ">=", error="@south_north_mismatch")

        dataset = Dataset({"north_lat": "34.56", "south_lat": "28.33"}, [])

        self.assertIsNone(rule.eval(dataset))

    def test_float_larger_equal_error(self):
        rule = MetaFieldCompareRule("north_lat", "south_lat", ">=", error="@south_north_mismatch")

        dataset = Dataset({"north_lat": "11.56", "south_lat": "28.33"}, [])

        issue = rule.eval(dataset)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_ERROR, issue.type)
        self.assertEqual("@south_north_mismatch", issue.description)

    def test_float_not_equal_warning(self):
        rule = MetaFieldCompareRule("north_lat", "south_lat", "!=", warning="should not be equal")

        dataset = Dataset({"north_lat": "28.33", "south_lat": "28.33"}, [])

        issue = rule.eval(dataset)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_WARNING, issue.type)
        self.assertEqual("should not be equal", issue.description)

    def test_int_less_than_error(self):
        rule = MetaFieldCompareRule("int_1", "int_2", "<", warning="should be smaller")

        dataset = Dataset({"int_1": "16", "int_2": "15"}, [])

        issue = rule.eval(dataset)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_WARNING, issue.type)
        self.assertEqual("should be smaller", issue.description)

    def test_int_equal_invalid_field(self):
        rule = MetaFieldCompareRule("int_1", "int_2", "==", error="must be same")

        dataset = Dataset({"int_1": "16"}, [])

        issue = rule.eval(dataset)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_ERROR, issue.type)
        self.assertEqual("Requested field not contained in metadata: int_2", issue.description)
