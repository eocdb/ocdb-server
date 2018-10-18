import builtins
import os
from contextlib import contextmanager
from typing import List, Dict, Union, Tuple

from eocdb.core import UNDEFINED
from .model import OpenAPI, Operation, Schema, Parameter, Property

TAB = "    "


class Code:
    """
    Generates Python code from a valid(!) OpenAPI 3.0.0 document.

    See also

    * https://swagger.io/docs/specification
    * https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md

    """

    def __init__(self, part: Union[str, list, "Code"] = None):
        self._indent = 0
        self._lines = []
        if part is not None:
            self.append(part)

    @contextmanager
    def indent(self):
        try:
            self.inc_indent()
            yield self._indent
        finally:
            self.dec_indent()

    def inc_indent(self):
        self._indent += 1

    def dec_indent(self):
        self._indent -= 1

    def append(self, part: Union[str, list, "Code"] = None) -> "Code":
        if isinstance(part, Code):
            self.append(part.lines)
        elif isinstance(part, list):
            for line in part:
                self.append(line)
        elif isinstance(part, str):
            tabs = self._indent * TAB
            self._lines.append(tabs + part)
        elif part is None:
            self._lines.append("")
        else:
            raise TypeError(f'part of unsupported type {type(part)}')
        return self

    @property
    def lines(self) -> List[str]:
        return self._lines


Modules = Dict[str, Code]
Packages = Dict[str, Modules]


class CodeWriter:
    @classmethod
    def write_packages(cls, base_dir: str, packages: Packages):
        for package, modules in packages.items():
            cls.write_modules(base_dir, package, modules)

    @classmethod
    def write_modules(cls, base_dir: str, package: str, modules: Modules):
        package_dir = os.path.join(base_dir, *package.split("."))
        os.makedirs(package_dir, exist_ok=True)
        for module_name, module_code in modules.items():
            cls.write_module(package_dir, module_name, module_code)

    @classmethod
    def write_module(cls, package_dir: str, module_name: str, code: Code):
        with open(os.path.join(package_dir, module_name + ".py"), "w") as fp:
            fp.writelines(line + "\n" for line in code.lines)


class CodeGen:
    def __init__(self, openapi: OpenAPI, prod_package: str, test_package: str = None):
        self._openapi = openapi
        self._prod_package = prod_package
        self._test_package = test_package

    @classmethod
    def gen_code(cls, openapi: OpenAPI, prod_package: str, test_package: str = None) -> Packages:
        code_gen = CodeGen(openapi, prod_package, test_package=test_package)
        packages = dict()
        code_gen._gen_handlers(packages)
        code_gen._gen_controllers(packages)
        code_gen._gen_models(packages)
        if test_package:
            code_gen._gen_handlers_tests(packages)
            code_gen._gen_controllers_tests(packages)
            code_gen._gen_models_tests(packages)
        return packages

    def _gen_handlers(self, packages: Packages):
        modules = dict()
        modules["__init__"] = self._gen_new_code_module().append("from ._mappings import MAPPINGS")
        modules["_handlers"] = self._gen_handlers_code()
        modules["_mappings"] = self._gen_mappings_code()
        packages[self._prod_package + ".handlers"] = modules

    def _gen_handlers_tests(self, packages: Packages):
        modules = dict()
        modules["__init__"] = self._gen_new_code_module()
        modules["test_handlers"] = self._gen_handlers_tests_code()
        packages[self._test_package + ".handlers"] = modules

    def _gen_controllers(self, packages: Packages):
        modules = dict()
        modules["__init__"] = self._gen_new_code_module()
        for path_item in self._openapi.path_items:
            for op in path_item.operations:
                self._gen_controller_code(op, path_item.path, modules)
        packages[self._prod_package + ".controllers"] = modules

    def _gen_controllers_tests(self, packages: Packages):
        modules = dict()
        modules["__init__"] = self._gen_new_code_module()
        for path_item in self._openapi.path_items:
            for op in path_item.operations:
                self._gen_controller_test_code(op, path_item.path, modules)
        packages[self._test_package + ".controllers"] = modules

    def _gen_models(self, packages: Packages):
        modules = dict()
        modules["__init__"] = self._gen_new_code_module()
        for schema_name, schema in self._openapi.components.schemas.items():
            self._gen_model_code(schema_name, schema, modules)
        packages[self._prod_package + ".models"] = modules

    def _gen_models_tests(self, packages: Packages):
        modules = dict()
        modules["__init__"] = self._gen_new_code_module()
        for schema_name, schema in self._openapi.components.schemas.items():
            self._gen_model_tests_code(schema_name, schema, modules)
        packages[self._test_package + ".models"] = modules

    def _gen_handlers_code(self) -> Code:
        code = self._gen_new_code_module()
        code.append("import tornado.escape")
        code.append()
        code.append("from ..webservice import WsRequestHandler")
        code.append("from ..reqparams import RequestParams")
        code.append(self._gen_controller_imports())
        code.append(self._gen_model_imports())

        for path_item in self._openapi.path_items:

            # Request class definition
            #
            class_name = _get_py_handler_class_name(path_item.path)
            code.append()
            code.append()
            code.append("# noinspection PyAbstractClass,PyShadowingBuiltins")
            code.append(f"class {class_name}(WsRequestHandler):")
            with code.indent():
                for op in path_item.operations:

                    # HTTP method declaration
                    #
                    path_params = [p for p in op.parameters if p.in_ == "path"]
                    path_params_str_parts = []
                    for path_param in path_params:
                        path_params_str_parts.append(f"{path_param.name}: str")
                    path_params_str = ", ".join(path_params_str_parts)
                    code.append()
                    if path_params_str:
                        code.append(f"def {op.method}(self, {path_params_str}):")
                    else:
                        code.append(f"def {op.method}(self):")

                    with code.indent():
                        # HTTP method docs
                        #
                        if op.operation_id:
                            code.append(f'"""Provide API operation {op.operation_id}()."""')

                        req_mime_type, req_schema = _select_handled_mime_type_and_schema_from_request_body(op)
                        req_py_type_name = _get_py_type_name(req_schema) if req_schema else None

                        res_mime_type, res_schema = _select_handled_mime_type_and_schema_from_response(op)
                        res_py_type_name = _get_py_type_name(res_schema) if res_schema else None

                        # Get and convert parameters
                        #
                        req_params, opt_params = _split_req_and_opt_parameters(op)
                        for param in req_params:
                            code.append(self._gen_fetch_param_code(param))
                        for param in opt_params:
                            code.append(self._gen_fetch_param_code(param))

                        # Get request body data
                        #
                        if req_py_type_name:
                            code.append(
                                f"# transform body with mime-type {req_mime_type} into a {req_py_type_name}")
                            if req_mime_type == "application/json":
                                if req_py_type_name == "Dict":
                                    code.append(f"data = tornado.escape.json_decode(self.request.body)")
                                else:
                                    code.append(f"data_dict = tornado.escape.json_decode(self.request.body)")
                                    code.append(f"data = {req_py_type_name}.from_dict(data_dict)")
                            elif req_mime_type == "text/plain":
                                code.append(f"data = self.request.body")
                            elif req_mime_type is not None:
                                code.append(f"# TODO (generated): transform self.request.body first")
                                code.append(f"data = self.request.body")
                            code.append()

                        # Call controller operation
                        #
                        func_name = _get_py_op_func_name(op, class_name)
                        call_args_parts = []
                        for param in req_params:
                            py_name = _get_py_lower_name(param.name, esc_builtins=True)
                            call_args_parts.append(f"{py_name}={py_name}")
                        if req_py_type_name is not None:
                            call_args_parts.append(f"data=data")
                        for param in opt_params:
                            py_name = _get_py_lower_name(param.name, esc_builtins=True)
                            call_args_parts.append(f"{py_name}={py_name}")
                        call_args = ", ".join(call_args_parts)
                        if call_args:
                            code.append(f"result = {func_name}(self.ws_context, {call_args})")
                        else:
                            code.append(f"result = {func_name}(self.ws_context)")

                        # Convert controller operation's return value
                        #
                        if res_py_type_name:
                            code.append()
                            code.append(f"# transform result of type {res_py_type_name}"
                                        f" into response with mime-type {res_mime_type}")
                            if res_mime_type == "application/json":
                                code.append(f"self.set_header('Content-Type', '{res_mime_type}')")
                                if res_py_type_name in {"bool", "str", "int", "float", "List", "Dict"}:
                                    code.append(f"self.finish(tornado.escape.json_encode(result))")
                                else:
                                    code.append(f"self.finish(tornado.escape.json_encode(result.to_dict()))")
                            elif res_mime_type == "text/plain":
                                code.append(f"self.set_header('Content-Type', '{res_mime_type}')")
                                code.append(f"self.finish(result)")
                            elif res_mime_type is not None:
                                code.append(f"# TODO (generated): transform result first")
                                code.append(f"self.finish(result)")
                            else:
                                code.append(f"self.finish()")
                        else:
                            code.append(f"self.finish()")

        return code

    def _gen_handlers_tests_code(self) -> Code:
        code = self._gen_new_code_module()
        code.append("import unittest")
        code.append("import urllib.parse")
        code.append()
        code.append("import tornado.escape")
        code.append("import tornado.testing")
        code.append()

        code.append(f"from {self._prod_package}.app import new_application")
        code.append(f"from ..helpers import new_test_service_context")

        code.append()
        code.append()
        code.append("class WsTestCase(tornado.testing.AsyncHTTPTestCase):")
        with code.indent():
            code.append("def get_app(self):")
            with code.indent():
                code.append('"""Implements AsyncHTTPTestCase.get_app()."""')
                code.append("application = new_application()")
                code.append("application.ws_context = new_test_service_context()")
                code.append("return application")
            code.append()
            code.append("@property")
            code.append("def ctx(self):")
            with code.indent():
                code.append("return self._app.ws_context")

        for path_item in self._openapi.path_items:

            # Request class definition
            #
            class_name = _get_py_handler_class_name(path_item.path)
            code.append()
            code.append()
            code.append(f"class {class_name}Test(WsTestCase):")
            with code.indent():

                for op in path_item.operations:

                    # HTTP method declaration
                    #
                    code.append()
                    code.append("@unittest.skip('not implemented yet')")
                    code.append(f"def test_{op.method}(self):")

                    with code.indent():
                        path_params = [p for p in op.parameters if p.in_ == "path"]
                        if path_params:
                            code.append()
                            code.append("# TODO (generated): set path parameter(s) to reasonable value(s)")
                            for param in path_params:
                                code.append(f"{param.name} = None")

                        query_params = [p for p in op.parameters if p.in_ == "query"]
                        if query_params:
                            code.append()
                            code.append("# TODO (generated): set query parameter(s) to reasonable value(s)")
                            for param in query_params:
                                code.append(f"{param.name} = None")

                        req_mime_type, req_schema = _select_handled_mime_type_and_schema_from_request_body(op)
                        if req_schema:
                            code.append()
                            code.append("# TODO (generated): set data for request body to reasonable value")
                            if req_schema.type == "array" and req_mime_type == "application/json":
                                code.append("data = []")
                                code.append("body = tornado.escape.json_encode(data)")
                            elif req_schema.type == "object" and req_mime_type == "application/json":
                                code.append("data = {}")
                                code.append("body = tornado.escape.json_encode(data)")
                            else:
                                code.append("data = None")
                                code.append("body = data")

                        method_part = f', method={repr(op.method.upper())}'
                        body_part = ', body=body' if req_schema else ''
                        if query_params:
                            dict_items = ", ".join([f"{p.name}={p.name}" for p in query_params])
                            code.append(f"query = urllib.parse.urlencode(dict({dict_items}))")
                            query_part = "?{query}"
                            url_part = f'f\"{path_item.path}{query_part}\"'
                        else:
                            url_part = f'f\"{path_item.path}\"'

                        code.append()
                        code.append(f"response = self.fetch({url_part}{method_part}{body_part})")
                        code.append("self.assertEqual(200, response.code)")
                        code.append("self.assertEqual('OK', response.reason)")

                        res_mime_type, res_schema = _select_handled_mime_type_and_schema_from_response(op)
                        code.append()
                        code.append("# TODO (generated): set expected_response correctly")
                        if res_schema:
                            if res_schema.type == "array" and res_mime_type == "application/json":
                                code.append("expected_response_data = []")
                                code.append("actual_response_data = []")
                                code.append(f"actual_response_data = tornado.escape.json_decode(response.body)")
                            elif res_schema.type == "object" and res_mime_type == "application/json":
                                code.append("expected_response_data = {}")
                                code.append(f"actual_response_data = tornado.escape.json_decode(response.body)")
                            else:
                                code.append(f"expected_response_data = None")
                                code.append(f"actual_response_data = response.body")
                        else:
                            code.append(f"expected_response_data = None")
                            code.append(f"actual_response_data = response.body")

                        code.append("self.assertEqual(expected_response_data, actual_response_data)")

        return code

    def _gen_controller_code(self, op: Operation, path: str, module_code: Dict[str, Code]):

        module_name = _get_py_op_module_name(op)
        class_name = _get_py_handler_class_name(path)
        func_name = _get_py_op_func_name(op, class_name)

        if module_name in module_code:
            code = module_code[module_name]
        else:
            code = self._gen_new_code_module()
            module_code[module_name] = code
            code.append("from typing import Dict, List")
            code.append()
            code.append("from ..context import WsContext")
            code.append(self._gen_model_imports())
            code.append(self._gen_assert_imports())

        req_params, opt_params = _split_req_and_opt_parameters(op)

        req_mime_type, req_schema = _select_handled_mime_type_and_schema_from_request_body(op)
        req_py_type_name = _get_py_type_name(req_schema) if req_schema else None

        res_mime_type, res_schema = _select_handled_mime_type_and_schema_from_response(op)
        res_py_type_name = _get_py_type_name(res_schema) if res_schema else None

        py_return_type_code = f" -> {res_py_type_name}" if res_py_type_name else ""

        code.append()
        code.append()
        code.append("# noinspection PyUnusedLocal")
        params_decls = []
        for p in req_params:
            py_name = _get_py_lower_name(p.name, esc_builtins=True)
            py_type = _get_py_type_name(p.schema)
            params_decls.append((py_name, py_type, UNDEFINED))
        if req_py_type_name:
            params_decls.append(("data", req_py_type_name, UNDEFINED))
        for p in opt_params:
            py_name = _get_py_lower_name(p.name, esc_builtins=True)
            py_type = _get_py_type_name(p.schema)
            py_default = p.schema.default if p.schema.default is not UNDEFINED else None
            params_decls.append((py_name, py_type, py_default))

        if params_decls:
            code.append(f"def {func_name}(ctx: WsContext,")
            prefix = " " * (len(func_name) + 5)
            for i in range(len(params_decls)):
                py_name, py_type, py_default = params_decls[i]
                postfix = "," if i < len(params_decls) - 1 else f"){py_return_type_code}:"
                if py_default is UNDEFINED:
                    code.append(f"{prefix}{py_name}: {py_type}{postfix}")
                else:
                    code.append(f"{prefix}{py_name}: {py_type} = {repr(py_default)}{postfix}")

            with code.indent():
                for p in op.parameters:
                    code.append(self._gen_param_validation_code(p))
        else:
            code.append(f"def {func_name}(ctx: WsContext){py_return_type_code}:")

        with code.indent():
            code.append(f"# TODO (generated): implement operation {func_name}()")
            code.append(f"raise NotImplementedError('operation {func_name}() not yet implemented')")

    def _gen_controller_test_code(self, op: Operation, path: str, module_code: Dict[str, Code]):

        module_name = "test_" + _get_py_op_module_name(op)
        test_class_name = _get_py_op_test_class_name(op)
        handler_class_name = _get_py_handler_class_name(path)
        func_name = _get_py_op_func_name(op, handler_class_name)

        if module_name in module_code:
            code = module_code[module_name]
        else:
            code = self._gen_new_code_module()
            module_code[module_name] = code
            code.append("import unittest")
            code.append()
            code.append(self._gen_controller_imports(package=self._prod_package + ".controllers"))
            code.append(self._gen_model_imports(package=self._prod_package + ".models"))
            code.append(f"from ..helpers import new_test_service_context")
            code.append()
            code.append()
            code.append(f"class {test_class_name}(unittest.TestCase):")
            code.append()
            with code.indent():
                code.append("def setUp(self):")
                with code.indent():
                    code.append("self.ctx = new_test_service_context()")

        with code.indent():
            code.append()
            code.append("@unittest.skip('not implemented yet')")
            code.append(f"def test_{func_name}(self):")
            with code.indent():
                req_params, opt_params = _split_req_and_opt_parameters(op)

                if req_params:
                    code.append("# TODO (generated): set required parameters")
                    for param in req_params:
                        py_name = _get_py_lower_name(param.name, esc_builtins=True)
                        code.append(f"{py_name} = None")

                req_mime_type, req_schema = _select_handled_mime_type_and_schema_from_request_body(op)
                if req_schema:
                    if req_schema.type == "array":
                        code.append("# TODO (generated): set request data list items")
                        code.append(f"data = []")
                    elif req_schema.type == "object":
                        if req_schema.ref_name:
                            code.append(f"data = {req_schema.ref_name}()")
                            code.append("# TODO (generated): set request data properties")
                        else:
                            code.append("# TODO (generated): set request data dict items")
                            code.append("data = {}")
                    else:
                        code.append("# TODO (generated): set data")
                        code.append("data = None")

                if opt_params:
                    code.append("# TODO (generated): set optional parameters")
                    for param in opt_params:
                        py_name = _get_py_lower_name(param.name, esc_builtins=True)
                        code.append(f"{py_name} = None")

                call_param_parts = []
                for param in req_params:
                    py_name = _get_py_lower_name(param.name, esc_builtins=True)
                    call_param_parts.append(f"{py_name}")

                if req_schema:
                    call_param_parts.append(f"data=data")

                for param in opt_params:
                    py_name = _get_py_lower_name(param.name, esc_builtins=True)
                    call_param_parts.append(f"{py_name}={py_name}")

                call_params = ", ".join(call_param_parts)

                code.append()
                if call_params:
                    code.append(f"result = {func_name}(self.ctx, {call_params})")
                else:
                    code.append(f"result = {func_name}(self.ctx)")

                res_mime_type, res_schema = _select_handled_mime_type_and_schema_from_response(op)
                if res_schema:
                    if res_schema.type == "array":
                        code.append("self.assertIsInstance(result, list)")
                        code.append("# TODO (generated): set expected result")
                        code.append("expected_result = []")
                        code.append("self.assertEqual(expected_result, result)")
                    elif res_schema.type == "object":
                        if res_schema.ref_name:
                            code.append(f"self.assertIsInstance(result, {res_schema.ref_name})")
                            code.append(f"expected_result = {res_schema.ref_name}()")
                            code.append("# TODO (generated): set expected result properties")
                            code.append("self.assertEqual(expected_result, result)")
                        else:
                            code.append(f"self.assertIsInstance(result, dict)")
                            code.append("# TODO (generated): set expected result")
                            code.append("expected_result = {}")
                            code.append("self.assertEqual(expected_result, result)")
                    else:
                        code.append("# TODO (generated): set expected result")
                        code.append("expected_result = None")
                        code.append("self.assertEqual(expected_result, result)")
                else:
                    code.append("self.assertIsNone(result)")

    def _gen_controller_imports(self, package: str = "..controllers") -> Code:
        module_names = set()
        for path_item in self._openapi.path_items:
            for op in path_item.operations:
                module_name = _get_py_op_module_name(op)
                module_names.add(module_name)
        code = Code()
        for module_name in sorted(module_names):
            code.append(f"from {package}.{module_name} import *")
        return code

    def _gen_model_imports(self, package: str = "..models", excluded_schema_name: str = None) -> Code:
        schema_names = set(schema_name for schema_name in self._openapi.components.schemas
                           if not excluded_schema_name or excluded_schema_name != schema_name)
        code = Code()
        for schema_name in sorted(schema_names):
            code.append(f"from {package}.{_get_py_lower_name(schema_name)} import {schema_name}")
        return code

    @classmethod
    def _gen_fetch_param_code(cls, param) -> Code:
        py_name = _get_py_lower_name(param.name, esc_builtins=True)
        py_type = _get_py_type_name(param.schema)
        if py_type == "str":
            type_suffix = ""
        elif py_type == "List[str]":
            type_suffix = "_list"
        elif py_type == "List[bool]":
            type_suffix = "_bool_list"
        elif py_type == "List[int]":
            type_suffix = "_int_list"
        elif py_type == "List[float]":
            type_suffix = "_float_list"
        else:
            type_suffix = "_" + py_type
        source = param.in_
        if source == "path":
            if py_type == "str":
                if py_name != param.name:
                    return Code(f"{py_name} = {param.name}")
                else:
                    return Code()
            else:
                return Code(f"{py_name} = RequestParams.to{type_suffix}('{param.name}', {param.name})")
        else:
            return Code(f"{py_name} = self.{source}.get_param{type_suffix}('{param.name}', "
                        f"default={repr(param.schema.default)})")

    def _gen_model_code(self, schema_name: str, schema: Schema, module_code: Dict[str, Code]):
        module_name = _get_py_lower_name(schema_name, esc_builtins=True)
        class_name = _get_py_camel_name(schema_name)

        if module_name in module_code:
            code = module_code[module_name]
        else:
            code = self._gen_new_code_module()
            module_code[module_name] = code
            code.append("from typing import Dict, List, Optional")
            code.append()
            code.append("from ..model import Model")
            code.append(self._gen_model_imports(package="", excluded_schema_name=schema_name))
            code.append(self._gen_assert_imports())

        if schema.properties:
            for p in schema.properties:
                if p.schema.enum:
                    code.append()
                    name_prefix = _get_py_upper_name(schema_name) + "_" + _get_py_upper_name(p.name)
                    for e in p.schema.enum:
                        e_name = str(e).replace(' ', '_').replace('-', '_').upper()
                        code.append(f"{name_prefix}_{e_name} = {repr(e)}")

        code.append()
        code.append()
        code.append(f"class {class_name}(Model):")
        with code.indent():
            code.append('"""')
            if schema.description:
                code.append(schema.description)
            else:
                code.append(f'The {class_name} model.')
            code.append('"""')

            code.append()
            if schema.properties:
                req_props, _opt_props = _split_req_and_opt_properties(schema)
                param_decls = []
                for p in req_props:
                    py_name = _get_py_lower_name(p.name, esc_builtins=True)
                    py_type = _get_py_type_name(p.schema)
                    param_decls.append((py_name, py_type, UNDEFINED))
                for p in _opt_props:
                    py_name = _get_py_lower_name(p.name, esc_builtins=True)
                    py_type = _get_py_type_name(p.schema)
                    py_default = p.schema.default if p.schema.default is not UNDEFINED else None
                    param_decls.append((py_name, py_type, py_default))
                code.append(f"def __init__(self,")
                prefix = 13 * " "
                for i in range(len(param_decls)):
                    py_name, py_type, py_default = param_decls[i]
                    postfix = "," if i < len(param_decls) - 1 else "):"
                    if py_default is UNDEFINED:
                        code.append(f"{prefix}{py_name}: {py_type}{postfix}")
                    else:
                        code.append(f"{prefix}{py_name}: {py_type} = {repr(py_default)}{postfix}")

            with code.indent():
                if schema.properties:
                    for p in schema.properties:
                        code.append(self._gen_param_validation_code(self._prop_to_param(p, schema)))
                    for p in schema.properties:
                        py_param_name = _get_py_lower_name(p.name, esc_builtins=True)
                        py_prop_name = _get_py_lower_name(p.name, esc_builtins=False)
                        code.append(f"self._{py_prop_name} = {py_param_name}")
                else:
                    code.append(f"pass")

            if schema.properties:
                for p in schema.properties:
                    py_name = _get_py_lower_name(p.name, esc_builtins=False)
                    py_type = _get_py_type_name(p.schema)
                    required = schema.required and p.name in schema.required
                    if not required:
                        py_type = f"Optional[{py_type}]"
                    code.append()
                    code.append(f"@property")
                    code.append(f"def {py_name}(self) -> {py_type}:")
                    with code.indent():
                        code.append(f"return self._{py_name}")

                    code.append()
                    code.append(f"@{py_name}.setter")
                    code.append(f"def {py_name}(self, value: {py_type}):")
                    with code.indent():
                        code.append(self._gen_param_validation_code(self._prop_to_param(p, schema, name="value")))
                        code.append(f"self._{py_name} = value")

    @classmethod
    def _prop_to_param(cls, prop: Property, schema: Schema, name: str = None) -> Parameter:
        return Parameter(name=name if name else prop.name,
                         schema=prop.schema,
                         in_="query",
                         required=schema.required
                                  and prop.name in schema.required)

    def _gen_model_tests_code(self, schema_name: str, schema: Schema, modules: Dict[str, Code]):
        # Should generate test code here, but models are actually just stupid object structures
        pass

    def _gen_mappings_code(self) -> Code:
        code = self._gen_new_code_module()
        code.append("from ._handlers import *")
        code.append("from ..webservice import url_pattern")
        code.append()
        code.append("MAPPINGS = [")
        with code.indent():
            for path_item in self._openapi.path_items:
                class_name = _get_py_handler_class_name(path_item.path)
                code.append(f"(url_pattern('{path_item.path}'), {class_name}),")
        code.append("]")
        return code

    @classmethod
    def _gen_param_validation_code(cls, param: Parameter) -> Code:
        code = Code()
        nullable = not param.required or param.schema.nullable
        py_param_name = _get_py_lower_name(param.name, esc_builtins=True)
        if not nullable and not param.allow_empty_value:
            code.append(f"assert_not_none_not_empty({py_param_name}, name='{py_param_name}')")
        elif not nullable:
            code.append(f"assert_not_none({py_param_name}, name='{py_param_name}')")
        elif not param.allow_empty_value:
            code.append(f"assert_not_empty({py_param_name}, name='{py_param_name}')")
        if param.schema.enum:
            code.append(f"assert_one_of({py_param_name}, {repr(param.schema.enum)}, name='{py_param_name}')")
        return code

    @classmethod
    def _gen_new_code_module(cls) -> Code:
        code = Code(_LICENSE_AND_COPYRIGHT)
        code.append()
        code.append()
        return code

    def _gen_assert_imports(self) -> Code:
        return Code("from ...core.asserts import"
                    " assert_not_empty,"
                    " assert_not_none,"
                    " assert_not_none_not_empty,"
                    " assert_one_of")


_TYPE_TO_PY_TYPE_MAP = dict(string="str", number="float", boolean="bool", integer="int", array='List', object="Dict")


def _get_py_op_module_name(op: Operation):
    return op.tags[0].lower() if op.tags and len(op.tags) else "default"


def _get_py_op_test_class_name(op: Operation):
    return _get_py_camel_name(op.tags[0]) + "Test" if op.tags and len(op.tags) else "Test"


def _get_py_type_name(schema: Schema) -> str:
    if schema.ref_name:
        return schema.ref_name

    if schema.type == 'array':
        item_schema = schema.items
        if item_schema:
            py_item_type = _get_py_type_name(item_schema)
            return f"List[{py_item_type}]"

    return _TYPE_TO_PY_TYPE_MAP[schema.type]


def _select_handled_mime_type_and_schema_from_request_body(op: Operation):
    req_mime_type = req_schema = None
    if op.request_body and op.request_body.content:
        req_mime_type, req_schema = _select_handled_mime_type_and_schema(op.request_body.content)
    return req_mime_type, req_schema


def _select_handled_mime_type_and_schema_from_response(op: Operation):
    res_mime_type = res_schema = None
    if op.responses:
        response = op.responses.get("200") or op.responses.get("default")
        if response and response.content:
            res_mime_type, res_schema = _select_handled_mime_type_and_schema(response.content)
    return res_mime_type, res_schema


def _select_handled_mime_type_and_schema(content: Dict[str, Schema]) -> Tuple[str, Schema]:
    if not content:
        raise ValueError("empty content")
    json_schema = content.get("application/json")
    if json_schema:
        return "application/json", json_schema
    json_schema = content.get("text/json")
    if json_schema:
        return "application/json", json_schema
    json_schema = content.get("text/plain")
    if json_schema:
        return "text/plain", json_schema
    json_schema = content.get("multipart/form-data")
    if json_schema:
        return "multipart/form-data", json_schema
    json_schema = content.get("application/octet-stream")
    if json_schema:
        return "application/octet-stream", json_schema
    raise ValueError(f'content with only unsupported mime-type(s): {set(content.keys())}')


def _get_py_lower_name(name: str, esc_builtins: bool = False):
    """Gen name for Python packages, modules, functions, methods, properties, variables."""
    py_name = ''
    n = len(name)
    for i in range(n):
        c = name[i]
        if c.islower() and i < n - 1 and name[i + 1].isupper():
            py_name += c
            py_name += "_"
        else:
            py_name += c.lower()
    if esc_builtins and hasattr(builtins, py_name):
        py_name += '_'
    return py_name


def _get_py_upper_name(name: str):
    """Gen name for Python constants."""
    return _get_py_lower_name(name).upper()


def _get_py_camel_name(s: str):
    """Gen name for Python classes."""
    n = len(s)
    if n == 0:
        return s
    s2 = s[0].upper()
    for i in range(1, n):
        c = s[i]
        if s[i - 1] == "_":
            s2 += c.upper()
        elif c != '_':
            s2 += c
    return s2


def _get_py_handler_class_name(path: str) -> str:
    if path.startswith('/'):
        path = path[1:]
    return _get_py_camel_name(path.replace('/', '_').replace('{', '').replace('}', '').lower())


def _get_py_op_func_name(op: Operation, class_name: str):
    return _get_py_lower_name(op.operation_id if op.operation_id else op.method + class_name, esc_builtins=True)


def _split_req_and_opt_parameters(op: Operation) -> Tuple[List[Parameter], List[Parameter]]:
    required_params = []
    optional_params = []
    if op.parameters:
        for p in op.parameters:
            if p.required or p.in_ == "path" or p.schema.default is UNDEFINED:
                required_params.append(p)
            else:
                optional_params.append(p)
    return required_params, optional_params


def _split_req_and_opt_properties(schema: Schema) -> Tuple[List[Property], List[Property]]:
    required_props = []
    optional_props = []
    if schema.properties:
        for p in schema.properties:
            if schema.required and p.name in schema.required:
                required_props.append(p)
            else:
                optional_props.append(p)
    return required_props, optional_props


_LICENSE_AND_COPYRIGHT = """# The MIT License (MIT)
# Copyright (c) 2018 by EUMETSAT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE."""
