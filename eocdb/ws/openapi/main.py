import os

from eocdb.ws.openapi.codegen import CodeGen
from eocdb.ws.openapi.parser import Parser


def main():
    file = os.path.join(os.path.dirname(__file__), "..", "res", "openapi.yml")
    openapi = Parser.from_yaml(file)
    CodeGen(openapi, "eocdb.ws").gen_code("_openapi_stubs")


if __name__ == "__main__":
    main()
