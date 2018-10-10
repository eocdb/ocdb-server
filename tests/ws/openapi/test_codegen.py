import unittest
import os

from eocdb.ws.openapi.parser import Parser
from eocdb.ws.openapi.codegen import CodeGen


class CodeGenTest(unittest.TestCase):
    def test_gen_code(self):
        file = os.path.join(os.path.dirname(__file__), "..", "..", "eocdb", "ws", "res", "openapi.yml")

        open_api = Parser.from_yaml(file)
        self.assertIsNotNone(open_api)

        code_gen = CodeGen(open_api)
        code_gen.gen_code()

