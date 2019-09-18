import unittest

from ocdb.core.models import Dataset, ISSUE_TYPE_ERROR
from ocdb.core.val._meta_field_required_rule import MetaFieldRequiredRule
from tests.core.val._mock_library import MockLibrary


class MetaFieldRequiredRuleTest(unittest.TestCase):

    def setUp(self):
        self._lib = MockLibrary()

    def test_field_present(self):
        rule = MetaFieldRequiredRule("investigator", "@required_field_missing")

        dataset = Dataset({"investigator": "Hans_Dampf"}, [])

        self.assertIsNone(rule.eval(dataset, self._lib))

    def test_field_missing(self):
        rule = MetaFieldRequiredRule("investigator", "@required_field_missing")

        dataset = Dataset({"a_not_tested_field": "Hans_Dampf"}, [])

        issue = rule.eval(dataset, self._lib)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_ERROR, issue.type)
        self.assertEqual("@required_field_missing", issue.description)

    def test_field_empty(self):
        rule = MetaFieldRequiredRule("investigator", "@required_field_missing")

        dataset = Dataset({"investigator": ""}, [])

        issue = rule.eval(dataset, self._lib)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_ERROR, issue.type)
        self.assertEqual("@required_field_missing", issue.description)