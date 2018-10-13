import unittest

from eocdb.core.asserts import *


class AssertsTest(unittest.TestCase):

    def test_assert_not_none(self):
        assert_not_none(3, "bibo")
        assert_not_none(True, "bibo")
        assert_not_none(False, "bibo")
        assert_not_none("", "bibo")
        assert_not_none("x", "bibo")
        assert_not_none(list(), "bibo")
        assert_not_none(dict(), "bibo")
        assert_not_none(set(), "bibo")
        with self.assertRaises(ValueError) as cm:
            assert_not_none(None, "bibo")
        self.assertEqual("bibo must not be None", f"{cm.exception}")

    def test_assert_not_empty(self):
        assert_not_empty(3, "bibo")
        assert_not_empty(True, "bibo")
        assert_not_empty(False, "bibo")
        assert_not_empty(None, "bibo")
        assert_not_empty("x", "bibo")
        assert_not_empty([1, 2], "bibo")
        assert_not_empty({"a": 1, "b": 2}, "bibo")
        assert_not_empty({"a", "b"}, "bibo")
        with self.assertRaises(ValueError) as cm:
            assert_not_empty("", "bibo")
        self.assertEqual("bibo must not be empty", f"{cm.exception}")
        with self.assertRaises(ValueError) as cm:
            assert_not_empty(list(), "bibo")
        self.assertEqual("bibo must not be empty", f"{cm.exception}")
        with self.assertRaises(ValueError) as cm:
            assert_not_empty(dict(), "bibo")
        self.assertEqual("bibo must not be empty", f"{cm.exception}")
        with self.assertRaises(ValueError) as cm:
            assert_not_empty(set(), "bibo")
        self.assertEqual("bibo must not be empty", f"{cm.exception}")

    def test_assert_not_none_not_empty(self):
        assert_not_none_not_empty(3, "bibo")
        assert_not_none_not_empty(True, "bibo")
        assert_not_none_not_empty(False, "bibo")
        assert_not_none_not_empty("x", "bibo")
        assert_not_none_not_empty([1, 2], "bibo")
        assert_not_none_not_empty({"a": 1, "b": 2}, "bibo")
        assert_not_none_not_empty({"a", "b"}, "bibo")
        with self.assertRaises(ValueError) as cm:
            assert_not_none_not_empty(None, "bibo")
        self.assertEqual("bibo must not be None", f"{cm.exception}")
        with self.assertRaises(ValueError) as cm:
            assert_not_none_not_empty("", "bibo")
        self.assertEqual("bibo must not be empty", f"{cm.exception}")

    def test_assert_one_of(self):
        assert_one_of(2, "bibo", [1, 2, 3])
        assert_one_of(2, "bibo", {1, 2, 3})

        with self.assertRaises(ValueError) as cm:
            assert_one_of(4, "bibo", {1, 2, 3})
        self.assertEqual("bibo must be one of {1, 2, 3}, but was 4", f"{cm.exception}")

        assert_one_of("c", "bibo", "abc")
        assert_one_of("c", "bibo", ["a", "b", "c"])
        assert_one_of("c", "bibo", {"a", "b", "c"})

        with self.assertRaises(ValueError) as cm:
            assert_one_of("d", "bibo", "abc")
        self.assertEqual("bibo must be one of 'abc', but was 'd'", f"{cm.exception}")
        with self.assertRaises(ValueError) as cm:
            assert_one_of("d", "bibo", ["a", "b", "c"])
        self.assertEqual("bibo must be one of ['a', 'b', 'c'], but was 'd'", f"{cm.exception}")
