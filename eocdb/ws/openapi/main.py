import os

from eocdb.ws.openapi.codegen import CodeGen, CodeWriter
from eocdb.ws.openapi.parser import Parser


def main():
    file = os.path.join(os.path.dirname(__file__), "..", "res", "openapi.yml")
    open_api = Parser.from_yaml(file)
    packages = CodeGen.gen_code(open_api, "eocdb.ws", "test.ws")
    CodeWriter.write_packages("_openapi_stubs", packages)


if __name__ == "__main__":
    main()
