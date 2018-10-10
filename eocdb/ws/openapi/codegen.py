import builtins
import os
from contextlib import contextmanager
from typing import List, Dict, Union, Tuple

from .model import OpenAPI, Operation, Schema, Parameter

TAB = "    "


class Code:
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

    def append(self, part: Union[str, list, "Code"] = None):
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
    def __init__(self, openapi: OpenAPI):
        self._openapi = openapi

    def gen_code(self, package: str) -> Packages:
        packages = dict()
        self._gen_handlers(package, packages)
        self._gen_controllers(package, packages)
        self._gen_models(package, packages)
        return packages

    def _gen_handlers(self, package: str, packages: Packages):
        modules = dict()
        modules["_handlers"] = self._gen_handler_code()
        modules["_mappings"] = self._gen_mappings_code()
        modules["__init__"] = Code("from ._mappings import MAPPINGS")
        packages[package + ".handlers"] = modules

    def _gen_controllers(self, package: str, packages: Packages):
        modules = dict()
        for path_item in self._openapi.path_items:
            for op in path_item.operations:
                self._gen_controller_code(op, path_item.path, modules)
        modules["__init__"] = Code()
        packages[package + ".controllers"] = modules

    def _gen_models(self, package: str, packages: Packages):
        modules = dict()
        for schema_name, schema in self._openapi.components.schemas.items():
            self._gen_model_code(schema_name, schema, modules)
        modules["__init__"] = Code()
        packages[package + ".models"] = modules

    def _gen_handler_code(self) -> Code:
        code = Code()

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

                        code.append("# noinspection PyBroadException,PyUnusedLocal")
                        code.append("try:")
                        with code.indent():

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
                                    code.append(f"# TODO: transform self.request.body first")
                                    code.append(f"data = self.request.body")
                                code.append()

                            # Call controller operation
                            #
                            func_name = _get_py_controller_func_name(op, class_name)
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
                                        code.append(f"self.write(tornado.escape.json_encode(result))")
                                    else:
                                        code.append(f"self.write(tornado.escape.json_encode(result.to_dict()))")
                                elif res_mime_type == "text/plain":
                                    code.append(f"self.set_header('Content-Type', '{res_mime_type}')")
                                    code.append(f"self.write(result)")
                                elif res_mime_type is not None:
                                    code.append(f"# TODO: transform result first")
                                    code.append(f"self.write(result)")
                                code.append()

                        code.append("except BaseException as e:")
                        with code.indent():
                            code.append("# TODO: handle error")
                            code.append("pass")
                            code.append()

                        code.append("finally:")
                        with code.indent():
                            code.append("self.finish()")

        return code

    def _gen_controller_code(self, op: Operation, path: str, module_code: Dict[str, Code]):

        module_name = _get_py_module_name(op)
        class_name = _get_py_handler_class_name(path)
        func_name = _get_py_controller_func_name(op, class_name)

        if module_name in module_code:
            code = module_code[module_name]
        else:
            code = Code()
            module_code[module_name] = code
            code.append("from typing import Dict, List")
            code.append()
            code.append("from ..context import WsContext")
            code.append(self._gen_model_imports())

        req_params, opt_params = _split_req_and_opt_parameters(op)

        req_mime_type, req_schema = _select_handled_mime_type_and_schema_from_request_body(op)
        req_py_type_name = _get_py_type_name(req_schema) if req_schema else None

        res_mime_type, res_schema = _select_handled_mime_type_and_schema_from_response(op)
        res_py_type_name = _get_py_type_name(res_schema) if res_schema else None

        param_decl_parts = []
        for parameter in req_params:
            py_name = _get_py_lower_name(parameter.name, esc_builtins=True)
            py_type = _get_py_type_name(parameter.schema)
            param_decl_parts.append(f"{py_name}: {py_type}")
        if req_py_type_name:
            param_decl_parts.append(f"data: {req_py_type_name}")
        for parameter in opt_params:
            py_name = _get_py_lower_name(parameter.name, esc_builtins=True)
            py_type = _get_py_type_name(parameter.schema)
            param_decl_parts.append(f"{py_name}: {py_type} = {repr(parameter.schema.default)}")
        param_decl = ", ".join(param_decl_parts)

        code.append()
        code.append()

        py_return_type_code = f" -> {res_py_type_name}" if res_py_type_name else ""
        if param_decl:
            code.append(f"def {func_name}(ctx: WsContext, {param_decl}){py_return_type_code}:")
        else:
            code.append(f"def {func_name}(ctx: WsContext){py_return_type_code}:")

        with code.indent():
            code.append(f"# return dict(code=200, status='OK')")
            code.append(f"raise NotImplementedError('operation {func_name}() not yet implemented')")

    def _gen_controller_imports(self) -> Code:
        module_names = set()
        for path_item in self._openapi.path_items:
            for op in path_item.operations:
                module_name = _get_py_module_name(op)
                module_names.add(module_name)
        code = Code()
        for module_name in sorted(module_names):
            code.append(f"from ..controllers.{module_name} import *")
        return code

    def _gen_model_imports(self) -> Code:
        schema_names = set(schema_name for schema_name in self._openapi.components.schemas)
        code = Code()
        for schema_name in sorted(schema_names):
            code.append(f"from ..models.{_get_py_lower_name(schema_name)} import {schema_name}")
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

    @classmethod
    def _gen_model_code(cls, schema_name: str, schema: Schema, module_code: Dict[str, Code]):
        module_name = _get_py_lower_name(schema_name, esc_builtins=True)
        class_name = _get_py_camel_name(schema_name)

        if module_name in module_code:
            code = module_code[module_name]
        else:
            code = Code()
            module_code[module_name] = code
            code.append("from typing import Dict, List")
            code.append()
            code.append("from ..model import Model")

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
            code.append(f"def __init__(self):")
            with code.indent():
                if schema.properties:
                    for prop in schema.properties:
                        py_name = _get_py_lower_name(prop.name, esc_builtins=False)
                        code.append(f"self._{py_name} = None")
                else:
                    code.append(f"pass")

            for prop in schema.properties:
                py_name = _get_py_lower_name(prop.name, esc_builtins=False)
                py_type = _get_py_type_name(prop.schema)
                code.append()
                code.append(f"@property")
                code.append(f"def {py_name}(self) -> {py_type}:")
                with code.indent():
                    code.append(f"return self._{py_name}")

                code.append()
                code.append(f"@{py_name}.setter")
                code.append(f"def {py_name}(self, value: {py_type}):")
                with code.indent():
                    code.append(f"self._{py_name} = value")

    def _gen_mappings_code(self) -> Code:
        code = Code()
        code.append("from ._handlers import *")
        code.append("from ..webservice import url_pattern")
        code.append()
        code.append()
        code.append("MAPPINGS = (")
        with code.indent():
            for path_item in self._openapi.path_items:
                class_name = _get_py_handler_class_name(path_item.path)
                code.append(f"(url_pattern('{path_item.path}'), {class_name}),")
        code.append(")")
        return code


_TYPE_TO_PY_TYPE_MAP = dict(string="str", number="float", boolean="bool", integer="int", array='List', object="Dict")


def _get_py_module_name(op: Operation):
    return op.tags[0].lower() if op.tags and len(op.tags) else "default"


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


def _get_py_camel_name(s: str):
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


def _get_py_controller_func_name(op: Operation, class_name: str):
    return _get_py_lower_name(op.operation_id if op.operation_id else op.method + class_name, esc_builtins=True)


def _split_req_and_opt_parameters(op: Operation) -> Tuple[List[Parameter], List[Parameter]]:
    required_params = []
    optional_params = []
    for parameter in op.parameters:
        if parameter.in_ == "path" or parameter.schema.default is None and parameter.schema.nullable:
            required_params.append(parameter)
        else:
            optional_params.append(parameter)
    return required_params, optional_params
