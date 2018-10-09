from io import IOBase
from typing import List, Dict, Union, Tuple

import os
import yaml
import builtins

from eocdb.core.asserts import *

TAB = "    "

Enum = Union[List[str], List[int], List[float]]
Number = Union[int, float]


class Property:
    def __init__(self, name: str, schema: "Schema"):
        assert_not_none_not_empty(name, "name")
        assert_not_none(schema, "schema")
        self._name = name
        self._schema = schema

    @property
    def name(self) -> str:
        return self._name

    @property
    def schema(self) -> "Schema":
        return self._schema


class Schema:
    def __init__(self,
                 type_: str,
                 format_: str = None,
                 items: "Schema" = None,
                 properties: List[Property] = None,
                 ref_name: str = None,
                 enum: Enum = None,
                 minimum: Number = None,
                 maximum: Number = None,
                 nullable: bool = False,
                 default: Any = None):
        assert_one_of(type_, "type", {"string", "number", "integer", "boolean", "array", "object"})
        assert_not_empty(ref_name, "ref_name")
        self._type = type_
        self._format = format_
        self._items = items
        self._properties = properties
        self._ref_name = ref_name
        self._enum = enum
        self._minimum = minimum
        self._maximum = maximum
        self._nullable = nullable
        self._default = default

    @property
    def type(self) -> str:
        return self._type

    @property
    def format(self) -> Optional[str]:
        return self._format

    @property
    def items(self) -> Optional["Schema"]:
        return self._items

    @property
    def properties(self) -> Optional[List[Property]]:
        return self._properties

    @property
    def ref_name(self) -> Optional[str]:
        return self._ref_name

    @property
    def enum(self) -> Optional[Enum]:
        return self._enum

    @property
    def minimum(self) -> Optional[Number]:
        return self._minimum

    @property
    def maximum(self) -> Optional[Number]:
        return self._maximum

    @property
    def nullable(self) -> bool:
        return self._nullable

    @property
    def default(self) -> Any:
        return self._default


class SchemaProxy(Schema):
    def __init__(self, type_: str):
        super().__init__(type_)
        self._delegate = None

    @property
    def delegate(self) -> Schema:
        return self._delegate

    @delegate.setter
    def delegate(self, value: Schema):
        self._delegate = value

    @property
    def type(self) -> str:
        return self.delegate.type

    @property
    def format(self) -> Optional[str]:
        return self.delegate.format

    @property
    def items(self) -> Optional["Schema"]:
        return self.delegate.items

    @property
    def properties(self) -> Optional[List[Property]]:
        return self.delegate.properties

    @property
    def ref_name(self) -> Optional[str]:
        return self.delegate.ref_name

    @property
    def enum(self) -> Optional[Enum]:
        return self.delegate.enum

    @property
    def minimum(self) -> Optional[Number]:
        return self.delegate.minimum

    @property
    def maximum(self) -> Optional[Number]:
        return self.delegate.maximum

    @property
    def nullable(self) -> bool:
        return self.delegate.nullable


class Component:
    def __init__(self, ref_name: str = None):
        assert_not_empty(ref_name, "ref_name")
        self._ref_name = ref_name

    @property
    def ref_name(self) -> Optional[str]:
        return self._ref_name


class Parameter(Component):
    def __init__(self,
                 name: str,
                 in_: str,
                 schema: Schema,
                 ref_name: str = None,
                 required: bool = False,
                 description: str = None):
        super().__init__(ref_name=ref_name)
        assert_not_none_not_empty(name, "name")
        assert_not_empty(name, "name")
        assert_one_of(in_, "in_", {"path", "query", "header", "cookie"})
        assert_not_none(schema, "schema")
        self._name = name
        self._ref_name = ref_name
        self._in = in_
        self._schema = schema
        self._required = required
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def ref_name(self) -> Optional[str]:
        return self._ref_name

    @property
    def in_(self) -> str:
        return self._in

    @property
    def schema(self) -> Schema:
        return self._schema

    @property
    def required(self) -> bool:
        return self._required

    @property
    def description(self) -> Optional[str]:
        return self._description


Content = Dict[str, Schema]


class DescribedContent(Component):
    def __init__(self,
                 content: Content,
                 ref_name: str = None,
                 description: str = None):
        super().__init__(ref_name=ref_name)
        assert_not_none(content, "content")
        self._content = content
        self._description = description

    @property
    def content(self) -> Content:
        return self._content

    @property
    def description(self) -> Optional[str]:
        return self._description


class RequestBody(DescribedContent):
    def __init__(self,
                 content: Content,
                 ref_name: str = None,
                 description: str = None,
                 required: bool = False):
        super().__init__(content, ref_name=ref_name, description=description)
        self._required = required

    @property
    def required(self) -> bool:
        return self._required


class Response(DescribedContent):
    def __init__(self,
                 content: Content,
                 ref_name: str = None,
                 description: str = None):
        super().__init__(content, ref_name=ref_name, description=description)


Responses = Dict[str, Response]


class Operation:
    def __init__(self,
                 method: str,
                 parameters: List[Parameter],
                 request_body: RequestBody = None,
                 responses: Responses = None,
                 operation_id: str = None,
                 tags: List[str] = None,
                 summary: str = None,
                 description: str = None):
        self._method = method
        self._operation_id = operation_id
        self._parameters = parameters
        self._request_body = request_body
        self._responses = responses
        self._tags = tags
        self._summary = summary
        self._description = description

    @property
    def method(self) -> str:
        return self._method

    @property
    def operation_id(self) -> str:
        return self._operation_id

    @property
    def parameters(self) -> Optional[List[Parameter]]:
        return self._parameters

    @property
    def request_body(self) -> Optional[RequestBody]:
        return self._request_body

    @property
    def responses(self) -> Optional[Responses]:
        return self._responses

    @property
    def tags(self) -> Optional[List[str]]:
        return self._tags

    @property
    def summary(self) -> Optional[str]:
        return self._summary

    @property
    def description(self) -> Optional[str]:
        return self._description


class PathItem:
    def __init__(self,
                 path: str,
                 operations: List[Operation],
                 summary: str = None,
                 description: str = None):
        assert_not_none(path, "path")
        assert_not_none(operations, "operations")
        self._path = path
        self._operations = operations
        self._summary = summary
        self._description = description

    @property
    def path(self) -> str:
        return self._path

    @property
    def operations(self) -> List[Operation]:
        return self._operations

    @property
    def summary(self) -> Optional[str]:
        return self._summary

    @property
    def description(self) -> Optional[str]:
        return self._description


class Components:
    def __init__(self):
        self._parameters = dict()
        self._responses = dict()
        self._request_bodies = dict()
        self._schemas = dict()

    @property
    def schemas(self) -> Dict[str, Schema]:
        return self._schemas

    @property
    def parameters(self) -> Dict[str, Parameter]:
        return self._parameters

    @property
    def responses(self) -> Dict[str, Response]:
        return self._responses

    @property
    def request_bodies(self) -> Dict[str, RequestBody]:
        return self._request_bodies


class OpenAPI:

    @classmethod
    def from_yaml(cls, file: Union[IOBase, str]) -> "OpenAPI":
        if isinstance(file, str):
            with open(file) as fp:
                yaml_dict = yaml.load(fp)
        else:
            yaml_dict = yaml.load(file)
        return cls.from_dict(yaml_dict)

    @classmethod
    def from_dict(cls, openapi_dict: Dict[str, Any]) -> "OpenAPI":
        version = openapi_dict.get("openapi")
        if version != "3.0.0":
            raise ValueError(f"Unsupported OpenAPI version {version}, must be 3.0.0")

        components = cls._parse_components(openapi_dict)
        path_items = cls._parse_path_items(openapi_dict, components)
        return OpenAPI(version, path_items, components)

    @classmethod
    def _parse_components(cls, openapi_dict: Dict[str, Any]) -> Components:
        components = Components()
        comp_dict = openapi_dict.get("components", {})

        schemas_dict = comp_dict.get("schemas", {})
        # Predefine all schemas by a proxy so object properties and array items can use schema references
        for ref_name, schema_dict in schemas_dict.items():
            components.schemas[ref_name] = SchemaProxy(schema_dict.get("type", "?"))
        # Then define each proxy
        for ref_name, schema_dict in schemas_dict.items():
            schema = cls._parse_schema(schema_dict, components, ref_name=ref_name)
            components.schemas[ref_name].delegate = schema

        parameters_dict = comp_dict.get("parameters", {})
        for ref_name, parameter_dict in parameters_dict.items():
            components.parameters[ref_name] = cls._parse_parameter(parameter_dict, components, ref_name=ref_name)

        request_bodies_dict = comp_dict.get("requestBodies", {})
        for ref_name, request_body_dict in request_bodies_dict.items():
            components.request_bodies[ref_name] = cls._parse_request_body(request_body_dict, components,
                                                                          ref_name=ref_name)

        responses_dict = comp_dict.get("responses", {})
        for ref_name, response_dict in responses_dict.items():
            components.responses[ref_name] = cls._parse_response(response_dict, components, ref_name=ref_name)

        return components

    @classmethod
    def _parse_path_items(cls,
                          openapi_dict: Dict[str, Any],
                          components: Components) -> List[PathItem]:
        paths_dict = openapi_dict.get("paths", {})
        if not paths_dict:
            raise ValueError(f"at least one path must be given in OpenAPI document")
        path_items = []
        for path, path_item_dict in paths_dict.items():
            path_item = cls._parse_path_item(path, path_item_dict, components)
            path_items.append(path_item)
        return path_items

    @classmethod
    def _parse_path_item(cls,
                         path: str,
                         path_item_dict: Dict[str, Any],
                         components: Components) -> PathItem:
        operations = []
        for method in ["get", "put", "post", "delete"]:
            op_dict = path_item_dict.get(method, {})
            if op_dict:
                operations.append(cls._parse_operation(method, op_dict, components))
        summary = path_item_dict.get("summary")
        description = path_item_dict.get("description")
        return PathItem(path, operations, summary=summary, description=description)

    @classmethod
    def _parse_operation(cls,
                         method: str,
                         op_dict: Dict[str, Any],
                         components: Components) -> Operation:
        parameter_dicts = op_dict.get("parameters", [])
        parameters = []
        for parameter_dict in parameter_dicts:
            parameters.append(cls._parse_parameter(parameter_dict, components))
        request_body_dict = op_dict.get("requestBody")
        request_body = None
        if request_body_dict:
            request_body = cls._parse_request_body(request_body_dict, components)
        responses_dict = op_dict.get("responses", {})
        responses = {}
        for status_code, response_dict in responses_dict.items():
            responses[status_code] = cls._parse_response(response_dict, components)
        return Operation(method,
                         parameters=parameters,
                         request_body=request_body,
                         responses=responses,
                         operation_id=op_dict.get("operationId"),
                         tags=op_dict.get("tags"),
                         summary=op_dict.get("summary"),
                         description=op_dict.get("description"))

    @classmethod
    def _parse_parameter(cls,
                         parameter_dict: Dict[str, Any],
                         components: Components,
                         ref_name: str = None) -> Parameter:
        ref = parameter_dict.get("$ref")
        if ref:
            ref_name = cls._parse_component_ref(ref, "parameters")
            parameter = components.parameters.get(ref_name)
            if parameter is None:
                raise ValueError(f"parameter reference not found: {ref}")
            return parameter
        name = parameter_dict.get("name")
        if not name:
            raise ValueError("missing 'name' in parameter")
        in_ = parameter_dict.get("in")
        if not in_:
            raise ValueError("missing 'in' in parameter")
        schema_dict = parameter_dict.get("schema")
        if not schema_dict:
            raise ValueError("missing 'schema' in parameter")
        schema = cls._parse_schema(schema_dict, components)
        return Parameter(name,
                         in_,
                         schema,
                         ref_name=ref_name,
                         required=parameter_dict.get("required", False),
                         description=parameter_dict.get("description"))

    @classmethod
    def _parse_schema(cls,
                      schema_dict: Dict[str, Any],
                      components: Components,
                      ref_name: str = None) -> Schema:
        ref = schema_dict.get("$ref")
        if ref:
            ref_name = cls._parse_component_ref(ref, "schemas")
            schema = components.schemas.get(ref_name)
            if schema is None:
                raise ValueError(f"schema reference not found: {ref}")
            return schema

        type_ = schema_dict.get("type")
        format_ = schema_dict.get("format")

        items_dict = schema_dict.get("items")
        items = None
        if items_dict:
            if type_ != "array":
                raise ValueError("'items' only allowed if 'type' is 'array'")
            items = cls._parse_schema(items_dict, components)

        properties_dict = schema_dict.get("properties")
        properties = None
        if properties_dict:
            if type_ != "object":
                raise ValueError("'properties' only allowed if 'type' is 'object'")
            properties = []
            for property_name, property_dict in properties_dict.items():
                property_schema = cls._parse_schema(property_dict, components)
                properties.append(Property(property_name, property_schema))

        return Schema(type_,
                      format_,
                      items=items,
                      properties=properties,
                      ref_name=ref_name,
                      enum=schema_dict.get("enum"),
                      minimum=schema_dict.get("minimum"),
                      maximum=schema_dict.get("maximum"),
                      nullable=schema_dict.get("nullable", False))

    @classmethod
    def _parse_request_body(cls,
                            request_body_dict: Dict[str, Any],
                            components: Components,
                            ref_name: str = None) -> RequestBody:
        ref = request_body_dict.get("$ref")
        if ref:
            ref_name = cls._parse_component_ref(ref, "requestBodies")
            request_body = components.request_bodies.get(ref_name)
            if request_body is None:
                raise ValueError(f"requestBody reference not found: {ref}")
            return request_body

        content_dict = request_body_dict.get("content")
        if not content_dict:
            raise ValueError("missing 'content' in 'requestBody'")
        content = cls._parse_content(content_dict, components)

        return RequestBody(content,
                           ref_name=ref_name,
                           description=request_body_dict.get("description"),
                           required=request_body_dict.get("required", False))

    @classmethod
    def _parse_response(cls,
                        response_dict: Dict[str, Any],
                        components: Components,
                        ref_name: str = None) -> Response:
        ref = response_dict.get("$ref")
        if ref:
            ref_name = cls._parse_component_ref(ref, "responses")
            response = components.responses.get(ref_name)
            if response is None:
                raise ValueError(f"response reference not found: {ref}")
            return response

        content_dict = response_dict.get("content", {})
        content = cls._parse_content(content_dict, components)

        return Response(content,
                        ref_name=ref_name,
                        description=response_dict.get("description"))

    @classmethod
    def _parse_content(cls, content_dict: Dict[str, Any], components: Components) -> Content:
        content = {}
        for mime_type, mime_type_dict in content_dict.items():
            schema_dict = mime_type_dict.get("schema")
            if not schema_dict:
                raise ValueError("missing 'schema' in 'content'")
            content[mime_type] = cls._parse_schema(schema_dict, components)
        return content

    @classmethod
    def _parse_component_ref(cls, ref: str, comp_name: str) -> Optional[str]:
        ref_parts = ref.split("/")
        if len(ref_parts) != 4 or ref_parts[0] != '#' or ref_parts[1] != 'components' or ref_parts[2] != comp_name:
            raise ValueError(f"invalid {comp_name} reference: {ref}")
        return ref_parts[3]

    def __init__(self,
                 version: str,
                 path_items: List[PathItem],
                 components: Components):
        assert_not_none_not_empty(version, "version")
        assert_not_none(path_items, "path_items")
        assert_not_none(components, "components")
        self._version = version
        self._path_items = path_items
        self._components = components

    @property
    def version(self) -> str:
        return self._version

    @property
    def path_items(self) -> List[PathItem]:
        return self._path_items

    @property
    def components(self) -> Components:
        return self._components


class Code:
    def __init__(self, part: Union[str, list, "Code"] = None):
        self._indent = 0
        self._lines = []
        if part is not None:
            self.append(part)

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
            self._lines.append(tabs + part + "\n")
        elif part is None:
            self._lines.append("\n")
        else:
            raise TypeError(f'part of unsupported type {type(part)}')

    @property
    def lines(self) -> List[str]:
        return self._lines


class CodeGen:
    def __init__(self, openapi: OpenAPI, package: str):
        self._openapi = openapi
        self._package = package

    def gen_code(self, base_dir: str):
        self._gen_handlers(base_dir)
        self._gen_controllers(base_dir)
        self._gen_models(base_dir)

    def _gen_controllers(self, base_dir: str):
        package = self._package + ".controllers"
        module_code = dict()
        for path_item in self._openapi.path_items:
            for op in path_item.operations:
                self._gen_controller_code(op, path_item.path, module_code)
        module_code["__init__"] = Code()
        self._write_code(base_dir, package, module_code)

    def _gen_models(self, base_dir: str):
        package = self._package + ".models"
        module_code = dict()
        for schema_name, schema in self._openapi.components.schemas.items():
            self._gen_model_code(schema_name, schema, module_code)
        module_code["__init__"] = Code()
        self._write_code(base_dir, package, module_code)

    def _gen_handlers(self, base_dir: str):
        package = self._package + ".handlers"
        module_code = dict()
        module_code["_handlers"] = self._gen_handler_code()
        module_code["_mappings"] = self._gen_mappings_code()
        module_code["__init__"] = Code("from ._mappings import MAPPINGS")
        self._write_code(base_dir, package, module_code)

    def _gen_handler_code(self) -> Code:
        code = Code()

        code.append("import tornado.escape")
        code.append()
        code.append("from ..webservice import WsRequestHandler")
        code.append("from ..reqparams import RequestParams")

        module_names = set()
        for path_item in self._openapi.path_items:
            for op in path_item.operations:
                module_name = _get_py_module_name(op)
                module_names.add(module_name)
        for module_name in sorted(module_names):
            code.append(f"from ..controllers.{module_name} import *")

        for path_item in self._openapi.path_items:
            class_name = _get_py_handler_class_name(path_item.path)

            code.append()
            code.append()
            code.append("# noinspection PyAbstractClass")
            code.append(f"class {class_name}(WsRequestHandler):")
            code.inc_indent()
            for op in path_item.operations:
                func_name = _get_py_controller_func_name(op, class_name)
                path_params = [p for p in op.parameters if p.in_ == "path"]

                path_params_str_parts = []
                for path_param in path_params:
                    py_type = _get_py_type_name(path_param.schema)
                    path_params_str_parts.append(f"{path_param.name}: {py_type}")
                path_params_str = ", ".join(path_params_str_parts)

                code.append()
                if path_params_str:
                    code.append(f"def {op.method}(self, {path_params_str}):")
                else:
                    code.append(f"def {op.method}(self):")
                code.inc_indent()

                if op.operation_id:
                    code.append(f'"""Provide API operation {op.operation_id}()."""')

                req_py_type = req_mime_type = None
                if op.request_body:
                    req_py_type, req_mime_type = _get_py_type_name_from_content(op.request_body.content)

                res_py_type = res_mime_type = None
                if op.responses:
                    response = op.responses.get("200") or op.responses.get("default")
                    if response:
                        res_py_type, res_mime_type = _get_py_type_name_from_content(response.content)

                if req_py_type:
                    code.append(f"# transform body with mime-type {req_mime_type} into a {req_py_type}")
                    if req_mime_type == "application/json":
                        if req_py_type == "Dict":
                            code.append(f"data = tornado.escape.json_decode(self.request.body)")
                        else:
                            code.append(f"data_dict = tornado.escape.json_decode(self.request.body)")
                            code.append(f"data = {req_py_type}.from_dict(data_dict)")
                    elif req_mime_type == "text/plain":
                        code.append(f"data = self.request.body")
                    elif req_mime_type is not None:
                        code.append(f"# TODO: data = transform(self.request.body)")
                    code.append()

                req_params, opt_params = _split_req_and_opt_parameters(op)

                for param in req_params:
                    code.append(self._gen_fetch_param_code(param))
                for param in opt_params:
                    code.append(self._gen_fetch_param_code(param))

                call_args_parts = []
                for param in req_params:
                    py_name = _get_py_lower_name(param.name, esc_builtins=True)
                    call_args_parts.append(f"{py_name}={py_name}")
                if req_py_type is not None:
                    call_args_parts.append(f"data=data")
                for param in opt_params:
                    py_name = _get_py_lower_name(param.name, esc_builtins=True)
                    call_args_parts.append(f"{py_name}={py_name}")
                call_args = ", ".join(call_args_parts)

                code.append("try:")
                code.inc_indent()

                if call_args:
                    code.append(f"result = {func_name}(self.ws_context, {call_args})")
                else:
                    code.append(f"result = {func_name}(self.ws_context)")

                if res_py_type:
                    code.append()
                    code.append(
                        f"# transform result of type {res_py_type} into response with mime-type {req_mime_type}")
                    if req_mime_type == "application/json":
                        code.append(f"self.set_header('Content-Type', 'application/json')")
                        if req_py_type == "Dict":
                            code.append(f"self.write(tornado.escape.json_encode(result))")
                        else:
                            code.append(f"self.write(tornado.escape.json_encode(result.to_dict()))")
                    elif req_mime_type == "text/plain":
                        code.append(f"self.write(result)")
                    elif req_mime_type is not None:
                        code.append(f"# TODO: self.write(transform(result))")
                    code.append()

                code.dec_indent()
                code.append(f"finally:")
                code.inc_indent()
                code.append(f"self.finish()")
                code.dec_indent()

                code.dec_indent()

            code.dec_indent()
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
                return Code(f"{py_name} = RequestParams.to{type_suffix}({param.name})")
        else:
            return Code(f"{py_name} = self.{source}.get_param{type_suffix}('{param.name}', "
                        f"default={repr(param.schema.default)})")

    @classmethod
    def _gen_controller_code(cls, op: Operation, path: str, module_code: Dict[str, Code]):

        module_name = _get_py_module_name(op)
        class_name = _get_py_handler_class_name(path)
        func_name = _get_py_controller_func_name(op, class_name)

        if module_name in module_code:
            code = module_code[module_name]
        else:
            code = Code(["from typing import List",
                         "",
                         "from ..context import WsContext"])
            module_code[module_name] = code

        req_params, opt_params = _split_req_and_opt_parameters(op)

        py_data_type_name = None
        if op.request_body:
            py_data_type_name, _ = _get_py_type_name_from_content(op.request_body.content)

        py_return_type_name = None
        if op.responses:
            response = op.responses.get("200") or op.responses.get("default")
            if response and response.content:
                py_return_type_name, _ = _get_py_type_name_from_content(response.content)

        param_decl_parts = []
        for parameter in req_params:
            py_name = _get_py_lower_name(parameter.name, esc_builtins=True)
            py_type = _get_py_type_name(parameter.schema)
            param_decl_parts.append(f"{py_name}: {py_type}")
        if py_data_type_name:
            param_decl_parts.append(f"data: {py_data_type_name}")
        for parameter in opt_params:
            py_name = _get_py_lower_name(parameter.name, esc_builtins=True)
            py_type = _get_py_type_name(parameter.schema)
            param_decl_parts.append(f"{py_name}: {py_type} = {repr(parameter.schema.default)}")
        param_decl = ", ".join(param_decl_parts)

        code.append()
        code.append()

        py_return_type_code = f" -> {py_return_type_name}" if py_return_type_name else ""
        if param_decl:
            code.append(f"def {func_name}(ctx: WsContext, {param_decl}){py_return_type_code}:")
        else:
            code.append(f"def {func_name}(ctx: WsContext){py_return_type_code}:")

        code.inc_indent()
        code.append(f"# return dict(code=200, status='OK')")
        code.append(f"raise NotImplementedError('operation {func_name}() not yet implemented')")
        code.dec_indent()

    @classmethod
    def _gen_model_code(cls, schema_name: str, schema: Schema, module_code: Dict[str, Code]):
        module_name = _get_py_lower_name(schema_name, esc_builtins=True)
        class_name = _get_py_camel_name(schema_name)

        if module_name in module_code:
            code = module_code[module_name]
        else:
            code = Code(["from typing import List",
                         "",
                         "from ..model import Model"])
            module_code[module_name] = code

        code.append()
        code.append()
        code.append(f"class {class_name}(Model):")
        code.inc_indent()

        code.append()
        code.append(f"def __init__(self):")
        code.inc_indent()
        if schema.properties:
            for prop in schema.properties:
                py_name = _get_py_lower_name(prop.name, esc_builtins=False)
                code.append(f"self._{py_name} = None")
        else:
            code.append(f"pass")
        code.dec_indent()

        for prop in schema.properties:
            py_name = _get_py_lower_name(prop.name, esc_builtins=False)
            py_type = _get_py_type_name(prop.schema)
            code.append()
            code.append(f"@property")
            code.append(f"def {py_name}(self) -> {py_type}:")
            code.inc_indent()
            code.append(f"return self._{py_name}")
            code.dec_indent()
            code.append()
            code.append(f"@{py_name}.setter")
            code.append(f"def {py_name}(self, value: {py_type}):")
            code.inc_indent()
            code.append(f"self._{py_name} = value")
            code.dec_indent()

        code.inc_indent()

    def _gen_mappings_code(self) -> Code:
        code = Code()
        code.append("from ._handlers import *")
        code.append("from ..webservice import url_pattern")
        code.append()
        code.append()
        code.append("MAPPINGS = (")
        code.inc_indent()
        for path_item in self._openapi.path_items:
            class_name = _get_py_handler_class_name(path_item.path)
            code.append(f"(url_pattern('{path_item.path}'), {class_name}),")
        code.dec_indent()
        code.append(")")
        return code

    @classmethod
    def _write_code(cls, base_dir: str, package: str, module_code: Dict[str, Code]):
        package_dir = os.path.join(base_dir, *package.split("."))
        os.makedirs(package_dir, exist_ok=True)
        for module_name in module_code:
            code = module_code[module_name]
            with open(os.path.join(package_dir, module_name + ".py"), "w") as fp:
                fp.writelines(code.lines)


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


def _get_py_type_name_from_content(content: Dict[str, Schema]) -> Tuple[str, str]:
    if not content:
        return "str", "text/plain"
    json_schema = content.get("application/json")
    if json_schema:
        return _get_py_type_name(json_schema), "application/json"
    json_schema = content.get("text/json")
    if json_schema:
        return _get_py_type_name(json_schema), "application/json"
    json_schema = content.get("text/plain")
    if json_schema:
        return "str", "text/plain"
    json_schema = content.get("multipart/form-data")
    if json_schema:
        return "Dict", "multipart/form-data"
    json_schema = content.get("application/octet-stream")
    if json_schema:
        return "io.BytesIO", "application/octet-stream"
    # TODO - check for binary files
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


def main():
    import os
    file = os.path.join(os.path.dirname(__file__), "res", "openapi.yml")
    openapi = OpenAPI.from_yaml(file)
    CodeGen(openapi, "eocdb.ws").gen_code("_openapi_stubs")


if __name__ == "__main__":
    main()
