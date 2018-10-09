import importlib
import os
from typing import List, Any, Dict, Tuple, Type

import yaml

from eocdb.ws.webservice import url_pattern

TAB = "    "


class OpenApi:

    def __init__(self, spec_path: str, package: str):
        file = os.path.join(os.path.dirname(__file__), spec_path.replace('/', os.path.sep))
        with open(file) as fp:
            spec = yaml.load(fp)
        spec_version = spec.get("openapi")
        if spec_version != "3.0.0":
            raise ValueError(f"Unsupported OpenAPI version {spec_version}, must be 3.0.0")
        self._spec = spec
        self._package = package
        self._operations = {}
        self._schemas = []
        self._resolve_operations()
        self._resolve_schemas()

    @property
    def spec(self) -> Dict[str, Any]:
        return self._spec

    @property
    def operations(self) -> Dict[str, List["Operation"]]:
        return self._operations

    @property
    def schemas(self) -> List["Schema"]:
        return self._schemas

    @property
    def path_mappings(self) -> List[Tuple[str, Type]]:
        path_mappings = []
        for path, ops in self._operations:
            class_name = _path_to_handler_name(path)
            module = importlib.import_module(self._package + ".handlers")
            handler_class = getattr(module, class_name)
            path_mappings.append((url_pattern(path), handler_class))
        return path_mappings

    def gen_code(self, base_dir: str):
        self._gen_handlers(base_dir)
        self._gen_controllers(base_dir)
        self._gen_models(base_dir)

    def _resolve_operations(self):
        paths = self._spec.get("paths")
        for path in paths:
            path_props = paths[path]
            self._resolve_op_method(path, path_props, "get")
            self._resolve_op_method(path, path_props, "put")
            self._resolve_op_method(path, path_props, "post")
            self._resolve_op_method(path, path_props, "delete")

    def _resolve_op_method(self, path: str, path_props: Dict[str, Any], method: str):
        method_props = path_props.get(method)
        if method_props is not None:
            self._resolve_op_method_props(path, method, method_props)

    def _resolve_op_method_props(self, path: str, method: str, method_props: Dict[str, Any]):
        operation_id = method_props.get("operationId")
        if not operation_id:
            raise ValueError(f"paths/'{path}'/{method}/operationId is required")
        tags = method_props.get("tags")
        if not tags:
            tags = ["default"]
        parameters = method_props.get("parameters", [])
        parameter_specs = []
        for i in range(len(parameters)):
            parameter = parameters[i]
            parameter = self._resolve_ref(parameter, expand=True)
            if "name" not in parameter:
                raise ValueError(f"paths/'{path}'/{method}/parameters/{i}/name is required")
            if "in" not in parameter:
                raise ValueError(f"paths/'{path}'/{method}/parameters/{i}/in is required")
            if "schema" not in parameter:
                raise ValueError(f"paths/'{path}'/{method}/parameters/{i}/schema is required")
            parameter_spec = dict(parameter)
            parameter_specs.append(parameter_spec)

        request_body_props = method_props.get("requestBody")
        request_body = None
        if request_body_props:
            request_body_props = self._resolve_ref(request_body_props, expand=True)
            content = request_body_props.get("content")
            if content:
                content = request_body_props.get("application/json")
                if content:
                    content = self._resolve_ref(content, expand=False)
                    if "schema" not in content:
                        raise ValueError(f"paths/'{path}'/{method}/requestBody/.../schema is required")
                    request_body = RequestBody(content["schema"],
                                               request_body_props.get("description"),
                                               request_body_props.get("required", False))
                content = request_body_props.get("multipart/form-data")
                if content:
                    content = self._resolve_ref(content, expand=False)
                    if "schema" not in content:
                        raise ValueError(f"paths/'{path}'/{method}/requestBody/.../schema is required")
                    request_body = RequestBody(content["schema"],
                                               request_body_props.get("description"),
                                               request_body_props.get("required", False))

        responses_dict = method_props.get("responses")
        responses = {}
        if responses_dict:
            responses_props = responses_dict.get("200") or responses_dict.get("default")
            if responses_props:
                content_dict = responses_props.get("content", {})
                for mime_type, mime_props in content_dict.items():
                    if mime_props:
                        mime_schema = mime_props.get('schema')
                        if mime_schema:
                            mime_schema = self._resolve_ref(mime_schema, expand=False)
                            # TODO: create Response with params
                            responses[mime_type] = Response()

        if path not in self._operations:
            self._operations[path] = []
        ops = self._operations[path]
        ops.append(Operation(path, method, tags[0], operation_id, parameter_specs, request_body, responses))

    def _resolve_schemas(self):
        components = self._spec.get("components")
        if not components or "schemas" not in components:
            return
        schemas = components.get("schemas")
        if not schemas:
            return

        for schema_name in schemas:
            schema_props = schemas[schema_name]
            schema_type = schema_props.get("type", "object")
            if schema_type != "object":
                raise ValueError(f"components/schemas/{schema_name}/type must be object")
            schema_required = schema_props.get("required", [])
            schema_props = schema_props.get("properties", {})
            resolved_schema_props = dict()
            for prop_name in schema_props:
                prop = schema_props[prop_name]
                prop = self._resolve_ref(prop, expand=False)
                resolved_schema_props[prop_name] = prop
            self._schemas.append(Schema(schema_name, schema_required, resolved_schema_props))

    def _resolve_ref(self, d: dict, expand: bool = False):
        ref = d.get("$ref")
        if ref:
            keys = ref.split('/')
            if len(keys) != 4 or keys[0] != '#':
                raise ValueError(f"invalid $ref: {ref}")
            keys = keys[1:]
            if expand:
                d = self._spec[keys[0]][keys[1]][keys[2]]
            else:
                d = dict(type=keys[2])
        return d

    def _gen_controllers(self, base_dir: str):
        package = self._package + ".controllers"
        module_code = dict()
        for _, ops in self._operations.items():
            for op in ops:
                op.gen_controller_code(module_code)
        module_code["__init__"] = ["\n"]
        self._write_code(base_dir, package, module_code)

    def _gen_models(self, base_dir: str):
        package = self._package + ".models"
        module_code = dict()
        for schema in self._schemas:
            schema.gen_code(module_code)
        module_code["__init__"] = ["\n"]
        self._write_code(base_dir, package, module_code)

    def _gen_handlers(self, base_dir: str):
        package = self._package + ".handlers"
        module_code = dict()
        module_code["_handlers"] = self._gen_handler_code()
        module_code["_mappings"] = self._gen_mappings_code()
        module_code["__init__"] = ["from ._mappings import MAPPINGS\n"]
        self._write_code(base_dir, package, module_code)

    def _gen_handler_code(self) -> List[str]:
        code = ["from ..webservice import WsRequestHandler\n",
                "from ..reqparams import RequestParams\n"]

        module_names = set()
        for path, ops in self._operations.items():
            for op in ops:
                module_name = op.tag.lower()
                module_names.add(module_name)
        for module_name in sorted(module_names):
            code.append(f"from ..controllers.{module_name} import *\n")

        for path, ops in self._operations.items():
            class_name = _path_to_handler_name(path)

            code.append("\n")
            code.append("\n")
            code.append("# noinspection PyAbstractClass\n")
            code.append(f"class {class_name}(WsRequestHandler):\n")
            for op in ops:
                func_name = _to_py_lower(op.operation_id)
                path_params = op.path_parameters

                path_params_str_parts = []
                for path_param in path_params:
                    name, _, data_type, _ = _get_name_type_default(path_param)
                    path_params_str_parts.append(f"{name}: {data_type}")
                path_params_str = ", ".join(path_params_str_parts)

                code.append("\n")
                if path_params_str:
                    code.append(f"{TAB}def {op.method}(self, {path_params_str}):\n")
                else:
                    code.append(f"{TAB}def {op.method}(self):\n")

                code.append(f'{TAB}{TAB}"""Provide API operation {op.operation_id}()."""\n')

                for param in op.parameters:
                    name, py_name, data_type, default_value = _get_name_type_default(param)
                    if data_type == "str":
                        type_suffix = ""
                    elif data_type == "List[str]":
                        type_suffix = "_list"
                    elif data_type == "List[bool]":
                        type_suffix = "_bool_list"
                    elif data_type == "List[int]":
                        type_suffix = "_int_list"
                    elif data_type == "List[float]":
                        type_suffix = "_float_list"
                    else:
                        type_suffix = "_" + data_type
                    source = param.get("in")
                    if source == "path":
                        if data_type == "str":
                            if py_name != name:
                                code.append(f"{TAB}{TAB}{py_name} = {name}\n")
                        else:
                            code.append(f"{TAB}{TAB}{py_name} = RequestParams.to{type_suffix}({name})\n")
                    else:
                        code.append(f"{TAB}{TAB}{py_name} = self.{source}.get_param{type_suffix}('{name}', "
                                    f"default={repr(default_value)})\n")

                call_args_parts = []
                for param in op.parameters:
                    name, py_name, _, _ = _get_name_type_default(param)
                    call_args_parts.append(f"{py_name}={py_name}")
                call_args = ", ".join(call_args_parts)

                code.append(f"{TAB}{TAB}self.set_header('Content-Type', 'text/json')\n")
                if call_args:
                    code.append(f"{TAB}{TAB}return {func_name}(self.ws_context, {call_args})\n")
                else:
                    code.append(f"{TAB}{TAB}return {func_name}(self.ws_context)\n")
        return code

    def _gen_mappings_code(self) -> List[str]:
        code = list()
        code.append("from ._handlers import *\n")
        code.append("from ..webservice import url_pattern\n")
        code.append("\n")
        code.append("\n")
        code.append("MAPPINGS = (\n")
        for path, ops in self.operations.items():
            class_name = _path_to_handler_name(path)
            code.append(f"{TAB}(url_pattern('{path}'), {class_name}),\n")
        code.append(")\n")
        return code

    @classmethod
    def _write_code(cls, base_dir: str, package: str, module_code: Dict[str, List[str]]):
        package_dir = os.path.join(base_dir, *package.split("."))
        os.makedirs(package_dir, exist_ok=True)
        for module_name in module_code:
            code = module_code[module_name]
            with open(os.path.join(package_dir, module_name + ".py"), "w") as fp:
                fp.writelines(code)


class RequestBody:
    def __init__(self, schema: Dict[str, Any], description: str, required: bool):
        self.schema = schema
        self.description = description
        self.required = required



class Response:
    pass


class Operation:
    def __init__(self,
                 path: str,
                 method: str,
                 tag: str,
                 operation_id: str,
                 parameters: List[Dict[str, Any]],
                 request_body: RequestBody,
                 responses: Dict[str, Response]):
        self.path = path
        self.method = method
        self.tag = tag
        self.operation_id = operation_id
        self.parameters = parameters
        self.request_body = request_body
        self.responses = responses

    @property
    def header_parameters(self) -> List[Dict]:
        return [p for p in self.parameters if p['in'] == 'header']

    @property
    def path_parameters(self) -> List[Dict]:
        return [p for p in self.parameters if p['in'] == 'path']

    @property
    def query_parameters(self) -> List[Dict]:
        return [p for p in self.parameters if p['in'] == 'query']

    @property
    def split_parameters(self) -> Tuple[List, List]:
        required_params = list(self.path_parameters)
        optional_params = list(self.header_parameters)
        for p in self.query_parameters:
            required = p.get("required", False)
            if required:
                required_params.append(p)
            else:
                optional_params.append(p)
        return required_params, optional_params

    def gen_controller_code(self, module_code: Dict[str, List[str]]):
        module_name = self.tag.lower()
        func_name = _to_py_lower(self.operation_id)

        if module_name in module_code:
            code = module_code[module_name]
        else:
            code = ["from typing import List\n",
                    "\n",
                    "from ..context import WsContext\n"]
            module_code[module_name] = code

        required_params, optional_params = self.split_parameters

        param_decl_parts = []
        for path_param in required_params:
            _, name, data_type, _ = _get_name_type_default(path_param)
            param_decl_parts.append(f"{name}: {data_type}")
        for path_param in optional_params:
            _, name, data_type, default_value = _get_name_type_default(path_param)
            param_decl_parts.append(f"{name}: {data_type} = {repr(default_value)}")
        param_decl = ", ".join(param_decl_parts)

        code.append("\n")
        code.append("\n")
        if param_decl:
            code.append(f"def {func_name}(ctx: WsContext, {param_decl}):\n")
        else:
            code.append(f"def {func_name}(ctx: WsContext):\n")

        code.append(f"    # TODO: implement operation {self.operation_id}\n")
        code.append(f"    return dict(code=200, status='OK')\n")

    def __str__(self):
        params = ', '.join(p['name'] for p in self.parameters)
        return f"{self.path} => {self.tag}.{self.operation_id}.{self.method}({params})"


class Schema:
    def __init__(self, name: str, required: List[str], properties: Dict[str, Dict[str, Any]]):
        self.name = name
        self.required = required
        self.properties = properties

    def gen_code(self, module_code: Dict[str, List[str]]):
        module_name = _to_py_lower(self.name)
        class_name = _to_py_camel(self.name)

        if module_name in module_code:
            code = module_code[module_name]
        else:
            code = ["from typing import List\n",
                    "\n",
                    "from ..model import Model\n"]
            module_code[module_name] = code

        code.append("\n")
        code.append("\n")
        code.append(f"class {class_name}(Model):\n")

        code.append("\n")
        code.append(f"{TAB}def __init__(self):\n")
        if self.properties:
            for prop_name in self.properties:
                prop_name = _to_py_lower(prop_name)
                code.append(f"{TAB}{TAB}self._{prop_name} = None\n")
        else:
            code.append(f"{TAB}{TAB}pass\n")

        for prop_name in self.properties:
            prop = self.properties[prop_name]
            _, prop_name, prop_type, _ = _get_name_type_default(prop, default_name=prop_name)
            code.append("\n")
            code.append(f"{TAB}@property\n")
            code.append(f"{TAB}def {prop_name}(self) -> {prop_type}:\n")
            code.append(f"{TAB}{TAB}return self._{prop_name}\n")
            code.append("\n")
            code.append(f"{TAB}@{prop_name}.setter\n")
            code.append(f"{TAB}def {prop_name}(self, value: {prop_type}):\n")
            code.append(f"{TAB}{TAB}self._{prop_name} = value\n")


_TYPE_MAPPING = dict(string="str", number="float", boolean="bool", integer="int", array='List')


def _to_py_type(type_name, default: str = None):
    return _TYPE_MAPPING.get(type_name, type_name if default is None else default)


def _to_py_lower(s: str):
    s2 = ''
    n = len(s)
    for i in range(n):
        c = s[i]
        if c.islower() and i < n - 1 and s[i + 1].isupper():
            s2 += c
            s2 += "_"
        else:
            s2 += c.lower()
    return s2


def _to_py_camel(s: str):
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


def _path_to_handler_name(path: str) -> str:
    if path.startswith('/'):
        path = path[1:]
    return _to_py_camel(path.replace('/', '_').replace('{', '').replace('}', '').lower())


def _get_name_type_default(param: Dict[str, Any],
                           default_name=None,
                           default_type="str") -> Tuple[str, str, str, Any]:
    name = param.get("name", default_name)
    py_name = _to_py_lower(name)
    schema = param.get("schema")
    data_type = _to_py_type(schema.get("type") if schema else param.get("type"), default=default_type)
    if data_type == 'List':
        items = schema.get("items") if schema else param.get("items")
        data_type = _to_py_type(items.get("type") if items else default_type, default=default_type)
        data_type = f"List[{data_type}]"
    default_value = schema.get("default") if schema else param.get("default")
    return name, py_name, data_type, default_value


def main():
    api = OpenApi("res/openapi.yml", "eocdb.ws")
    api.gen_code('_openapi_stubs')


if __name__ == "__main__":
    main()
