import unittest

from ocdb.core.asserts import *


class AssertsTest(unittest.TestCase):

    def test_assert_not_none(self):
        assert_not_none(3, name="bibo")
        assert_not_none(True, name="bibo")
        assert_not_none(False, name="bibo")
        assert_not_none("", name="bibo")
        assert_not_none("x", name="bibo")
        assert_not_none(list(), name="bibo")
        assert_not_none(dict(), name="bibo")
        assert_not_none(set(), name="bibo")
        with self.assertRaises(ValueError) as cm:
            assert_not_none(None, name="bibo")
        self.assertEqual("bibo must not be None", f"{cm.exception}")

    def test_assert_not_empty(self):
        assert_not_empty(3, name="bibo")
        assert_not_empty(True, name="bibo")
        assert_not_empty(False, name="bibo")
        assert_not_empty(None, name="bibo")
        assert_not_empty("x", name="bibo")
        assert_not_empty([1, 2], name="bibo")
        assert_not_empty({"a": 1, "b": 2}, name="bibo")
        assert_not_empty({"a", "b"}, name="bibo")
        with self.assertRaises(ValueError) as cm:
            assert_not_empty("", name="bibo")
        self.assertEqual("bibo must not be empty", f"{cm.exception}")
        with self.assertRaises(ValueError) as cm:
            assert_not_empty(list(), name="bibo")
        self.assertEqual("bibo must not be empty", f"{cm.exception}")
        with self.assertRaises(ValueError) as cm:
            assert_not_empty(dict(), name="bibo")
        self.assertEqual("bibo must not be empty", f"{cm.exception}")
        with self.assertRaises(ValueError) as cm:
            assert_not_empty(set(), name="bibo")
        self.assertEqual("bibo must not be empty", f"{cm.exception}")

    def test_assert_not_none_not_empty(self):
        assert_not_none_not_empty(3, name="bibo")
        assert_not_none_not_empty(True, name="bibo")
        assert_not_none_not_empty(False, name="bibo")
        assert_not_none_not_empty("x", name="bibo")
        assert_not_none_not_empty([1, 2], name="bibo")
        assert_not_none_not_empty({"a": 1, "b": 2}, name="bibo")
        assert_not_none_not_empty({"a", "b"}, name="bibo")
        with self.assertRaises(ValueError) as cm:
            assert_not_none_not_empty(None, name="bibo")
        self.assertEqual("bibo must not be None", f"{cm.exception}")
        with self.assertRaises(ValueError) as cm:
            assert_not_none_not_empty("", name="bibo")
        self.assertEqual("bibo must not be empty", f"{cm.exception}")

    def test_assert_one_of(self):
        assert_one_of(2, [1, 2, 3], name="bibo")
        assert_one_of(2, {1, 2, 3}, name="bibo")

        with self.assertRaises(ValueError) as cm:
            assert_one_of(4, {1, 2, 3}, name="bibo")
        self.assertEqual("bibo must be one of {1, 2, 3}, but was 4", f"{cm.exception}")

        assert_one_of("c", "abc", name="bibo")
        assert_one_of("c", ["a", "b", "c"], name="bibo")
        assert_one_of("c", {"a", "b", "c"}, name="bibo")

        with self.assertRaises(ValueError) as cm:
            assert_one_of("d", "abc", name="bibo")
        self.assertEqual("bibo must be one of 'abc', but was 'd'", f"{cm.exception}")
        with self.assertRaises(ValueError) as cm:
            assert_one_of("d", ["a", "b", "c"], name="bibo")
        self.assertEqual("bibo must be one of ['a', 'b', 'c'], but was 'd'", f"{cm.exception}")

    def test_assert_instance(self):
        assert_instance(["nasenmann"], [])
        assert_instance({"nasenmann": 456}, {})

        with self.assertRaises(ValueError) as cm:
            assert_instance(567, "")
        self.assertEqual("567 is not of type <class 'str'>", f"{cm.exception}")
