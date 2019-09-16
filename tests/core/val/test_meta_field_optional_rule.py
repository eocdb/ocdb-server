from unittest import TestCase

from ocdb.core.models import Dataset, ISSUE_TYPE_WARNING
from ocdb.core.val._meta_field_optional_rule import MetaFieldOptionalRule
from tests.core.val._mock_library import MockLibrary


class MetaFieldOptionalRuleTest(TestCase):

    def setUp(self):
        self._lib = MockLibrary()

    def test_field_missing(self):
        rule = MetaFieldOptionalRule("station", "@field_value_missing")

        dataset = Dataset({}, [])

        self.assertIsNone(rule.eval(dataset, self._lib))

    def test_field_present(self):
        rule = MetaFieldOptionalRule("station", "@field_value_missing")

        dataset = Dataset({"station": "Svalbard"}, [])

        self.assertIsNone(rule.eval(dataset, self._lib))

    def test_field_present_but_empty(self):
        rule = MetaFieldOptionalRule("station", "@field_value_missing")

        dataset = Dataset({"station": ""}, [])

        issue = rule.eval(dataset, self._lib)
        self.assertIsNotNone(issue)
        self.assertEqual(ISSUE_TYPE_WARNING, issue.type)
        self.assertEqual("@field_value_missing", issue.description)
