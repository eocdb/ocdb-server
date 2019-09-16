from unittest import TestCase

from ocdb.core.models import Dataset, ISSUE_TYPE_WARNING
from ocdb.core.val._meta_field_obsolete_rule import MetaFieldObsoleteRule
from tests.core.val._mock_library import MockLibrary


class MetaFieldObsoleteRuleTest(TestCase):

    def setUp(self):
        self._lib = MockLibrary()

    def test_field_missing(self):
        rule = MetaFieldObsoleteRule("station", "@field_obsolete")

        dataset = Dataset({}, [])

        self.assertIsNone(rule.eval(dataset, self._lib))

    def test_field_present(self):
        rule = MetaFieldObsoleteRule("station", "@field_obsolete")

        dataset = Dataset({"station": "whatever"}, [])

        issue = rule.eval(dataset, self._lib)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_WARNING, issue.type)
        self.assertEqual("@field_obsolete", issue.description)