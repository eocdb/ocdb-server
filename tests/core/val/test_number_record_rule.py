import unittest

from eocdb.core.models import ISSUE_TYPE_ERROR
from eocdb.core.val._number_record_rule import NumberRecordRule
from tests.core.val._mock_library import MockLibrary


class NumberRecordRuleTest(unittest.TestCase):

    def setUp(self):
        self._lib = MockLibrary()

    def test_pass_float_no_limits(self):
        rule = NumberRecordRule("a", "1/m", "@field_has_wrong_unit", "@field_out_of_bounds")

        issues = rule.eval("1/m", [23.4, 23.6, 22,7, 19.6], self._lib)
        self.assertIsNone(issues)

    def test_fail_wrong_unit(self):
        rule = NumberRecordRule("a", "1/inch", "@field_has_wrong_unit", "@field_out_of_bounds")

        issues = rule.eval("1/m", [23.4, 23.6, 22.7, 19.6], self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@field_has_wrong_unit", issues[0].description)

    def test_fail_value_out_of_lower_bound(self):
        rule = NumberRecordRule("a", "1/m", "@field_has_wrong_unit", "@field_out_of_bounds", lower_bound=12.5)

        issues = rule.eval("1/m", [23.4, 11.6, 22.7, 19.6], self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@field_out_of_bounds", issues[0].description)

    def test_fail_value_out_of_upper_bound(self):
        rule = NumberRecordRule("a", "1/m", "@field_has_wrong_unit", "@field_out_of_bounds", upper_bound=30.0)

        issues = rule.eval("1/m", [23.4, 11.6, 22.7, 33.7], self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@field_out_of_bounds", issues[0].description)

    def test_fail_value_out_of_both_bounds(self):
        rule = NumberRecordRule("a", "1/m", "@field_has_wrong_unit", "@field_out_of_bounds", lower_bound=24.5, upper_bound=30.0)

        issues = rule.eval("1/m", [23.4, 25.9, 29.1, 33.7], self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(2, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@field_out_of_bounds", issues[0].description)
        self.assertEqual(ISSUE_TYPE_ERROR, issues[1].type)
        self.assertEqual("@field_out_of_bounds", issues[1].description)


