import unittest

from eocdb.db.fields import get_fields


class GetFieldsTest(unittest.TestCase):

    def test_get_fields(self):
        fields = get_fields()
        self.assertIs(fields, get_fields())
        self.assertIsInstance(fields, list)
        self.assertEqual(361, len(fields))
        for field in fields:
            self.assertIsInstance(field, list)
            self.assertEqual(3, len(field))
            self.assertIsInstance(field[0], str)
            self.assertIsInstance(field[1], str)
            self.assertIsInstance(field[2], str)
            self.assertTrue(len(field[0]) > 0)
            self.assertTrue(len(field[1]) > 0)
            self.assertTrue(len(field[2]) > 0)
