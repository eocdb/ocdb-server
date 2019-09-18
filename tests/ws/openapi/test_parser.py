import os
import unittest

from ocdb.ws.openapi.parser import Parser


class ParserTest(unittest.TestCase):
    def test_from_yaml(self):
        file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ocdb", "ws", "res", "openapi.yml")

        openapi = Parser.from_yaml(file)
        self.assertIsNotNone(openapi)
        self.assertEqual(openapi.version, "3.0.0")

        # So far, this is just a smoke test
        self.assertIsNotNone(openapi.components)
        self.assertIsNotNone(openapi.components.schemas)
        self.assertEqual(16, len(openapi.components.schemas))
        self.assertIsNotNone(openapi.components.parameters)
        self.assertEqual(25, len(openapi.components.parameters))
        self.assertIsNotNone(openapi.components.request_bodies)
        self.assertEqual(9, len(openapi.components.request_bodies))
        self.assertIsNotNone(openapi.components.responses)
        self.assertEqual(17, len(openapi.components.responses))

        self.assertIsNotNone(openapi.path_items)
        self.assertEqual(29, len(openapi.path_items))
