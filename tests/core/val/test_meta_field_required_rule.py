import unittest

from eocdb.core.models import Dataset, ISSUE_TYPE_ERROR
from eocdb.core.val._meta_field_required_rule import MetaFieldRequiredRule


class MetaFieldRequiredRuleTest(unittest.TestCase):

    def test_field_present(self):
        rule = MetaFieldRequiredRule("investigator", "@required_field_missing")

        dataset = Dataset({"investigator": "Hans_Dampf"}, [])

        self.assertIsNone(rule.eval(dataset))

    def test_field_missing(self):
        rule = MetaFieldRequiredRule("investigator", "@required_field_missing")

        dataset = Dataset({"a_not_tested_field": "Hans_Dampf"}, [])

        issue = rule.eval(dataset)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_ERROR, issue.type)
        self.assertEqual("@required_field_missing", issue.description)

    def test_field_empty(self):
        rule = MetaFieldRequiredRule("investigator", "@required_field_missing")

        dataset = Dataset({"investigator": ""}, [])

        issue = rule.eval(dataset)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_ERROR, issue.type)
        self.assertEqual("@required_field_missing", issue.description)