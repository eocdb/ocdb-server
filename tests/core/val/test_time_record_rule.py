import unittest

from eocdb.core.models import ISSUE_TYPE_ERROR
from eocdb.core.val._time_record_rule import TimeRecordRule
from tests.core.val._mock_library import MockLibrary


class TimeRecordRuleTest(unittest.TestCase):

    def setUp(self):
        self._lib = MockLibrary()

    def test_pass(self):
        values = ["23:13:23", "12:59:24", "13:15:59"]
        rule = TimeRecordRule("a_name", "hh:mm:ss", "error")

        issues = rule.eval("hh:mm:ss", values, self._lib)
        self.assertIsNone(issues)

    def test_fail_not_parseable(self):
        values = ["11:13:23", "12:14:24", "AB:CD:25"]
        rule = TimeRecordRule("a_name", "hh:mm:ss", "error")

        issues = rule.eval("hh:mm:ss", values, self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@invalid_time_record", issues[0].description)

    def test_fail_hour_out_of_range(self):
        values = ["31:13:23", "12:14:24", "13:15:25"]
        rule = TimeRecordRule("a_name", "hh:mm:ss", "error")

        issues = rule.eval("hh:mm:ss", values, self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@invalid_time_value", issues[0].description)

    def test_fail_minute_out_of_range(self):
        values = ["11:13:23", "12:60:24", "13:15:25"]
        rule = TimeRecordRule("a_name", "hh:mm:ss", "error")

        issues = rule.eval("hh:mm:ss", values, self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@invalid_time_value", issues[0].description)

    def test_fail_second_out_of_range(self):
        values = ["11:13:23", "12:22:24", "13:15:71"]
        rule = TimeRecordRule("a_name", "hh:mm:ss", "error")

        issues = rule.eval("hh:mm:ss", values, self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@invalid_time_value", issues[0].description)

    def test_fail_invalid_unit(self):
        values = ["11:13:23", "12:22:24", "13:15:21"]
        rule = TimeRecordRule("a_name", "hh:mm:ss", "error_message")

        issues = rule.eval("Megazorks", values, self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("error_message", issues[0].description)

    def test_from_dict(self):
        rule_dict = {"name": "field_name", "unit": "long", "unit_error": "that_s_wrong"}

        rule = TimeRecordRule.from_dict(rule_dict)
        self.assertIsNotNone(rule)
        self.assertEqual("field_name", rule.name)
        self.assertEqual("long", rule.unit[0])
        self.assertEqual("that_s_wrong", rule.unit_error)