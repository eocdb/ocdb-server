import os
import unittest

from ocdb.ws.openapi.codegen import Code, CodeGen
from ocdb.ws.openapi.parser import Parser


class CodeGenTest(unittest.TestCase):
    def test_gen_code(self):
        file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ocdb", "ws", "res", "openapi.yml")

        open_api = Parser.from_yaml(file)
        self.assertIsNotNone(open_api)

        packages = CodeGen.gen_code(open_api, "ocdb.ws")
        self.assertIsNotNone(packages)
        self.assertEqual(3, len(packages))

        packages = CodeGen.gen_code(open_api, "ocdb.ws", "tests.ws")
        self.assertIsNotNone(packages)
        self.assertEqual(6, len(packages))


class CodeTest(unittest.TestCase):
    def test_append_code_str(self):
        code = Code()
        code.append("line1")
        with code.indent():
            code.append("line2")
            with code.indent():
                code.append("line3")
                code.append("line4")
            code.append("line5")
        code.append("line6")

        self.assertEqual(['line1',
                          '    line2',
                          '        line3',
                          '        line4',
                          '    line5',
                          'line6'],
                         code.lines)

    def test_append_code_code(self):
        inner_code = Code()
        inner_code.append("iline1")
        with inner_code.indent():
            inner_code.append("iline2")
            with inner_code.indent():
                inner_code.append("iline3")
                inner_code.append("iline4")
            inner_code.append("iline5")
        inner_code.append("iline6")

        outer_code = Code()
        outer_code.append(["# outer"])
        with outer_code.indent():
            outer_code.append(["# inner"])
            outer_code.append(inner_code)

        self.assertEqual(['# outer',
                          '    # inner',
                          '    iline1',
                          '        iline2',
                          '            iline3',
                          '            iline4',
                          '        iline5',
                          '    iline6'],
                         outer_code.lines)
