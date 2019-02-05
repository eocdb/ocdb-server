import unittest

from eocdb.core.models import Dataset, ISSUE_TYPE_WARNING
from eocdb.core.val._meta_field_optional_rule import MetaFieldOptionalRule


class MetaFieldOptionalRuleTest(unittest.TestCase):

    def test_field_missing(self):
        rule = MetaFieldOptionalRule("station", "@field_value_missing")

        dataset = Dataset({}, [])

        self.assertIsNone(rule.eval(dataset))

    def test_field_present(self):
        rule = MetaFieldOptionalRule("station", "@field_value_missing")

        dataset = Dataset({"station": "Svalbard"}, [])

        self.assertIsNone(rule.eval(dataset))

    def test_field_present_but_empty(self):
        rule = MetaFieldOptionalRule("station", "@field_value_missing")

        dataset = Dataset({"station": ""}, [])

        issue = rule.eval(dataset)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_WARNING, issue.type)
        self.assertEqual("@field_value_missing", issue.description)