import unittest

from ocdb.core.models import ISSUE_TYPE_ERROR
from ocdb.core.val._string_record_rule import StringRecordRule
from tests.core.val._mock_library import MockLibrary


class StringRecordRuleTest(unittest.TestCase):

    def setUp(self):
        self._lib = MockLibrary()

    def test_pass(self):
        values = ["maus", "hamster", "meerschwein"]
        rule = StringRecordRule("Papa", "error_message")

        issues = rule.eval("dontcare", values, self._lib)
        self.assertIsNone(issues)

    def test_fail_empty_field(self):
        values = ["maus", "", "meerschwein"]
        rule = StringRecordRule("Papa", "error_message")

        issues = rule.eval("dontcare", values, self._lib)
        self.assertIsNotNone(issues)
        self.assertEqual(1, len(issues))
        self.assertEqual(ISSUE_TYPE_ERROR, issues[0].type)
        self.assertEqual("error_message", issues[0].description)

    def test_from_dict(self):
        rule_dict = {"name": "Willem", "error": "wow_that_s_wrong"}

        rule = StringRecordRule.from_dict(rule_dict)
        self.assertIsNotNone(rule)
        self.assertEqual("Willem", rule.name)
        self.assertEqual("wow_that_s_wrong", rule.error)