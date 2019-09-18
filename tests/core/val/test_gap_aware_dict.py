from unittest import TestCase

from ocdb.core.val._gap_aware_dict import GapAwareDict


class GapAwareDictTest(TestCase):

    def test_the_dict(self):
        dict = GapAwareDict({"key_1": "a value"})

        self.assertEqual("a value", dict["key_1"])
        self.assertEqual("#MISSING_REFERENCE", dict["key_missing"])
