import unittest
from typing import List

from ocdb.db.static_data import get_products, get_product_groups, get_fields, get_groups_for_product


class StaticDataTest(unittest.TestCase):

    def test_get_product_groups(self):
        products_groups = get_product_groups()
        self.assertIsInstance(products_groups, list)
        self.assertTrue(len(products_groups) > 15)
        for product_group in products_groups:
            self.assertIsInstance(product_group, dict)
            self.assertEqual(3, len(product_group))
            self.assertIsInstance(product_group.get("name"), str)
            self.assertIsInstance(product_group.get("products"), list)
            self.assertIsInstance(product_group.get("description"), str)
        names = {pg["name"] for pg in products_groups}
        self.assertIn('a', names)
        self.assertIn('b', names)
        self.assertIn('Chl', names)

    def test_get_products(self):
        fields = get_products()
        self.assertIsInstance(fields, list)
        self.assertTrue(len(fields) > 300)
        for field in fields:
            self.assert_valid_field(field)
        names = {f["name"] for f in fields}
        self.assertIn('Chl', names)
        self.assertNotIn('lon', names)
        self.assertNotIn('lat', names)

    def test_get_fields(self):
        fields = get_fields()
        self.assertIs(fields, get_fields())
        self.assertIsInstance(fields, list)
        self.assertTrue(len(fields) > 300)
        for field in fields:
            self.assert_valid_field(field)
        names = {f["name"] for f in fields}
        self.assertIn('Chl', names)
        self.assertIn('lon', names)
        self.assertIn('lat', names)

    def test_get_group_for_product(self):
        self.assertEqual(["Chl"], get_groups_for_product("phaeo"))
        self.assertEqual(["HPLC"], get_groups_for_product("cantha"))

    def test_get_group_for_product_no_result(self):
        self.assertEqual([], get_groups_for_product("ungrouped_variable"))

    def test_get_group_for_product_numbers_stripped(self):
        self.assertEqual(["a"], get_groups_for_product("abs_ag676"))

    def assert_valid_field(self, field):
        self.assertIsInstance(field, dict)
        self.assertEqual(4, len(field))
        self.assertIsInstance(field.get("name"), str)
        self.assertIsInstance(field.get("units"), str)
        self.assertIsInstance(field.get("description"), str)
        self.assertIsInstance(field.get("groups"), List)
        self.assertTrue(len(field.get("name")) > 0)
        self.assertTrue(len(field.get("units")) > 0)
        self.assertTrue(len(field.get("description")) > 0)
        self.assertTrue(len(field.get("groups")) >= 0)
