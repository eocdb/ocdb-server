import math
import unittest

from ocdb.core.models import ISSUE_TYPE_ERROR
from ocdb.core.val._number_record_rule import NumberRecordRule
from tests.core.val._mock_library import MockLibrary


class NumberRecordRuleTest(unittest.TestCase):

    def setUp(self):
        self._lib = MockLibrary()

    def test_pass_float_no_limits(self):
        rule = NumberRecordRule("a", "1/m", "@field_has_wrong_unit", "@field_out_of_bounds")

        issues = rule.eval("1/m", [23.4, 23.6, 22, 7, 19.6], self._lib)
        self.assertIsNone(issues)

    def test_pass_float_with_missing_value(self):
        rule = NumberRecordRule("a", "1/m", "@field_has_wrong_unit", "@field_out_of_bounds", lower_bound=0.0)

        issues = rule.eval("1/m", [23.4, -9999.0, 22, 7, 19.6], self._lib, missing_value=-9999)
        self.assertIsNone(issues)

    def test_fail_wrong_unit(self):
        rule = NumberRecordRule("a", "1/inch", "@field_has_wrong_unit", "@field_out_of_bounds")

        issues = rule.eval("1/m", [23.4, 23.6, 22.7, 19.6], self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@field_has_wrong_unit", issues[0].description)

    def test_pass_two_units(self):
        rule = NumberRecordRule("b", "m^3,l", "@field_has_wrong_unit", "@field_out_of_bounds")

        issues = rule.eval("m^3", [23.4, 23.6, 22, 7, 19.6], self._lib)
        self.assertIsNone(issues)

        issues = rule.eval("l", [23.4, 23.6, 22, 7, 19.6], self._lib)
        self.assertIsNone(issues)

    def test_pass_none_unit_variations(self):
        rule = NumberRecordRule("b", "none", "@field_has_wrong_unit", "@field_out_of_bounds")

        issues = rule.eval("none", [23.4, 23.6, 22, 7, 19.6], self._lib)
        self.assertIsNone(issues)

        issues = rule.eval("unitless", [23.4, 23.6, 22, 7, 19.6], self._lib)
        self.assertIsNone(issues)

    def test_fail_value_out_of_lower_bound(self):
        rule = NumberRecordRule("a", "1/m", "@field_has_wrong_unit", "@field_out_of_bounds", lower_bound=12.5)

        issues = rule.eval("1/m", [23.4, 11.6, 22.7, 19.6], self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@field_out_of_bounds", issues[0].description)

    def test_fail_value_not_a_number(self):
        rule = NumberRecordRule("a", "1/m", "@field_has_wrong_unit", "@field_out_of_bounds", lower_bound=0)

        issues = rule.eval("1/m", [23.4, 11.6, "hasi", 19.6], self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@field_number_not_a_number", issues[0].description)

    def test_fail_value_out_of_upper_bound(self):
        rule = NumberRecordRule("a", "1/m", "@field_has_wrong_unit", "@field_out_of_bounds", upper_bound=30.0)

        issues = rule.eval("1/m", [23.4, 11.6, 22.7, 33.7], self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@field_out_of_bounds", issues[0].description)

    def test_fail_value_out_of_both_bounds(self):
        rule = NumberRecordRule("a", "1/m", "@field_has_wrong_unit", "@field_out_of_bounds", lower_bound=24.5,
                                upper_bound=30.0)

        issues = rule.eval("1/m", [23.4, 25.9, 29.1, 33.7], self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(2, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("@field_out_of_bounds", issues[0].description)
        self.assertEqual(ISSUE_TYPE_ERROR, issues[1].type)
        self.assertEqual("@field_out_of_bounds", issues[1].description)

    def test_from_dict(self):
        rule_dict = {"name": "Kalle", "unit": "%vol", "lower_bound": "17", "upper_bound": "189.45",
                     "value_error": "plain_wrong", "unit_error": "wtf"}

        rule = NumberRecordRule.from_dict(rule_dict)
        self.assertIsNotNone(rule)
        self.assertEqual("Kalle", rule.name)
        self.assertEqual(["%vol"], rule.units)
        self.assertEqual("wtf", rule.unit_error)
        self.assertEqual("plain_wrong", rule.value_error)
        self.assertAlmostEqual(17.0, rule.lower_bound, 8)
        self.assertAlmostEqual(189.45, rule.upper_bound, 8)

    def test_from_dict_no_upper_bound(self):
        rule_dict = {"name": "Lucy", "unit": "m^3", "lower_bound": "18.1", "value_error": "oha",
                     "unit_error": "no_not_this_one"}

        rule = NumberRecordRule.from_dict(rule_dict)
        self.assertIsNotNone(rule)
        self.assertEqual("Lucy", rule.name)
        self.assertEqual(["m^3"], rule.units)
        self.assertEqual("no_not_this_one", rule.unit_error)
        self.assertEqual("oha", rule.value_error)
        self.assertAlmostEqual(18.1, rule.lower_bound, 8)
        self.assertTrue(math.isinf(rule.upper_bound))

    def test_from_dict_no_lower_bound(self):
        rule_dict = {"name": "Herman", "unit": "unite", "upper_bound": "190.55", "value_error": "plain_wrong",
                     "unit_error": "wtf"}

        rule = NumberRecordRule.from_dict(rule_dict)
        self.assertIsNotNone(rule)
        self.assertEqual("Herman", rule.name)
        self.assertEqual(["unite"], rule.units)
        self.assertEqual("wtf", rule.unit_error)
        self.assertEqual("plain_wrong", rule.value_error)
        self.assertTrue(math.isinf(rule.lower_bound))
        self.assertAlmostEqual(190.55, rule.upper_bound, 8)

    def test_from_dict_no_error_messages(self):
        rule_dict = {"name": "Kalle", "unit": "%vol", "lower_bound": "17", "upper_bound": "189.45"}

        rule = NumberRecordRule.from_dict(rule_dict)
        self.assertIsNotNone(rule)
        self.assertEqual("Kalle", rule.name)
        self.assertEqual(["%vol"], rule.units)
        self.assertIsNone(rule.unit_error)
        self.assertIsNone(rule.value_error)
        self.assertAlmostEqual(17.0, rule.lower_bound, 8)
        self.assertAlmostEqual(189.45, rule.upper_bound, 8)

    def test_from_dict_two_units(self):
        rule_dict = {"name": "Kalle", "unit": "mg/m^3,ug/l", "lower_bound": "17", "upper_bound": "189.45",
                     "value_error": "plain_wrong", "unit_error": "wtf"}

        rule = NumberRecordRule.from_dict(rule_dict)
        self.assertIsNotNone(rule)
        self.assertEqual("Kalle", rule.name)
        self.assertEqual(["mg/m^3", "ug/l"], rule.units)
        self.assertEqual("wtf", rule.unit_error)
        self.assertEqual("plain_wrong", rule.value_error)
        self.assertAlmostEqual(17.0, rule.lower_bound, 8)
        self.assertAlmostEqual(189.45, rule.upper_bound, 8)
