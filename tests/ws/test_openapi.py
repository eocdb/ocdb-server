import unittest

from eocdb.ws.openapi import OpenApi


class OpenApiTest(unittest.TestCase):
    def test_init(self):
        api = OpenApi("res/openapi.yml", "eocdb.ws")
        self.assertIsNotNone(api.spec)
        self.assertEqual(api.spec.get("openapi"), "3.0.0")

        self.assertIsNotNone(api.schemas)
        self.assertEqual(8, len(api.schemas))

        self.assertIsNotNone(api.operations)
        self.assertEqual(14, len(api.operations))

        # self.assertIsNotNone(api.path_mappings)
        # self.assertEqual(21, len(api.path_mappings))
