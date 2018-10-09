import unittest
import os

from eocdb.ws.openapi import OpenAPI


class OpenApiTest(unittest.TestCase):
    def test_init(self):
        file = os.path.join(os.path.dirname(__file__), "..", "..", "eocdb", "ws", "res", "openapi.yml")

        openapi = OpenAPI.from_yaml(file)
        self.assertIsNotNone(openapi)
        self.assertEqual(openapi.version, "3.0.0")

        self.assertIsNotNone(openapi.components)
        self.assertIsNotNone(openapi.components.schemas)
        self.assertEqual(8, len(openapi.components.schemas))
        self.assertIsNotNone(openapi.components.parameters)
        self.assertEqual(10, len(openapi.components.parameters))
        self.assertIsNotNone(openapi.components.request_bodies)
        self.assertEqual(1, len(openapi.components.request_bodies))
        self.assertIsNotNone(openapi.components.responses)
        self.assertEqual(2, len(openapi.components.responses))

        self.assertIsNotNone(openapi.path_items)
        self.assertEqual(14, len(openapi.path_items))

