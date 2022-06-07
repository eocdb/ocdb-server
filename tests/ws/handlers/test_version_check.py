import unittest
from ocdb.ws.handlers._version_check import is_version_valid


class VersionNumberComparisonTest(unittest.TestCase):

    def test_that_equal_version_numbers_are_valid(self):
        self.assertTrue(is_version_valid("4.3.2", "4.3.2"))

    def test_that_10_is_bigger_than_2(self):
        self.assertTrue(is_version_valid("4.3.10", "4.3.2"))

    # def test_that_a_post_release_is_valid(self):
    #     post releases are currently not supported
    #     self.assertTrue(is_version_valid("4.3.post2", "4.3.2"))

    def test_that_a_smaller_version_numbers_is_invalid(self):
        self.assertFalse(is_version_valid("4.3.1", "4.3.2"))

    def test_that_a_development_version_is_less_than_min_version(self):
        self.assertFalse(is_version_valid("4.3.dev2", "4.3.2"))

    def test_that_an_alpha_version_is_less_than_min_version(self):
        self.assertFalse(is_version_valid("4.3.2a0", "4.3.2"))

    def test_that_a_beta_version_is_less_than_min_version(self):
        self.assertFalse(is_version_valid("4.3.2b0", "4.3.2"))

    def test_that_a_release_candidate_version_is_less_than_min_version(self):
        self.assertFalse(is_version_valid("4.3.2rc0", "4.3.2"))
