import unittest
import os

from eocdb.ws.openapi.parser import Parser


class ParserTest(unittest.TestCase):
    def test_from_yaml(self):
        file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "eocdb", "ws", "res", "openapi.yml")

        openapi = Parser.from_yaml(file)
        self.assertIsNotNone(openapi)
        self.assertEqual(openapi.version, "3.0.0")

        self.assertIsNotNone(openapi.components)
        self.assertIsNotNone(openapi.components.schemas)
        self.assertEqual(9, len(openapi.components.schemas))
        self.assertIsNotNone(openapi.components.parameters)
        self.assertEqual(19, len(openapi.components.parameters))
        self.assertIsNotNone(openapi.components.request_bodies)
        self.assertEqual(3, len(openapi.components.request_bodies))
        self.assertIsNotNone(openapi.components.responses)
        self.assertEqual(7, len(openapi.components.responses))

        self.assertIsNotNone(openapi.path_items)
        self.assertEqual(15, len(openapi.path_items))

