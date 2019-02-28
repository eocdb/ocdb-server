import unittest

from eocdb.core.models import ISSUE_TYPE_ERROR, ISSUE_TYPE_WARNING
from eocdb.core.val._date_record_rule import DateRecordRule
from tests.core.val._mock_library import MockLibrary


class DateRecordRuleTest(unittest.TestCase):

    def setUp(self):
        self._lib = MockLibrary()

    def test_pass(self):
        values = ["20050321", "20050322", "20050324"]
        rule = DateRecordRule("Papa", 1975)

        issues = rule.eval("dontcare", values, self._lib)
        self.assertIsNone(issues)

    def test_fail_incorrect_string_length(self):
        values = ["wot?", "20050322", "20050324"]
        rule = DateRecordRule("Mama", 1976)

        issues = rule.eval("whatever", values, self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@data_invalid_date", issues[0].description)

    def test_fail_unparseable_date(self):
        values = ["abcdefgh", "20050322", "20050324"]
        rule = DateRecordRule("Mama", 1977)

        issues = rule.eval("whatever", values, self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@data_invalid_date", issues[0].description)

    def test_fail_before_lower_bound(self):
        values = ["20050322", "20050322", "19660324"]
        rule = DateRecordRule("Mama", 1977)

        issues = rule.eval("whatever", values, self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@data_date_bounds_error", issues[0].description)

    def test_fail_month_out_of_bounds(self):
        values = ["20051422", "20050322", "20050324"]
        rule = DateRecordRule("Mama", 1977)

        issues = rule.eval("whatever", values, self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@data_invalid_month", issues[0].description)

    def test_fail_day_out_of_bounds(self):
        values = ["20050822", "20050332", "20050324"]
        rule = DateRecordRule("Mama", 1977)

        issues = rule.eval("whatever", values, self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@data_invalid_day_of_month", issues[0].description)

    def test_from_dict(self):
        rule_dict = {"name": "Martha", "min_year": 1999}

        rule = DateRecordRule.from_dict(rule_dict)
        self.assertIsNotNone(rule)
        self.assertEqual("Martha", rule.name)
        self.assertEqual(1999, rule.min_year)