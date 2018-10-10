import unittest

from eocdb.ws.openapi.model import SchemaProxy, SchemaImpl


class SchemaTest(unittest.TestCase):
    def test_schema_proxy(self):
        schema_proxy = SchemaProxy()
        schema_impl = SchemaImpl("array", items=SchemaImpl("number"))

        self.assertEqual("array", schema_impl.type)
        self.assertIsNotNone(schema_impl.items)
        self.assertEqual("number", schema_impl.items.type)

        with self.assertRaises(AttributeError):
            # noinspection PyUnusedLocal
            type_ = schema_proxy.type
        with self.assertRaises(AttributeError):
            # noinspection PyUnusedLocal
            items_ = schema_proxy.items

        schema_proxy.delegate = schema_impl

        self.assertEqual("array", schema_proxy.type)
        self.assertIsNotNone(schema_proxy.items)
        self.assertEqual("number", schema_proxy.items.type)
