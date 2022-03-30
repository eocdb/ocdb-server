from io import IOBase
from typing import List, Dict, Union

import yaml

from ocdb.core import UNDEFINED
from .model import OpenAPI, Parameter, RequestBody, Response, Property, Schema, SchemaImpl, SchemaProxy, \
    Content, Components, PathItem, Operation
from ...core.asserts import *


class Parser:
    """
    Parses an OpenAPI 3.0.0 document.

    See also

    * https://swagger.io/docs/specification
    * https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md

    """

    @classmethod
    def from_yaml(cls, file: Union[IOBase, str]) -> OpenAPI:
        if isinstance(file, str):
            with open(file) as fp:
                yaml_dict = yaml.safe_load(fp)
        else:
            yaml_dict = yaml.safe_load(file)
        return cls.from_dict(yaml_dict)

    @classmethod
    def from_dict(cls, openapi_dict: Dict[str, Any]) -> OpenAPI:
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
            components.schemas[ref_name] = SchemaProxy()
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
                         allow_empty_value=parameter_dict.get("allowEmptyValue", True),
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

        return SchemaImpl(type_,
                          format_,
                          items=items,
                          properties=properties,
                          ref_name=ref_name,
                          enum=schema_dict.get("enum"),
                          required=schema_dict.get("required"),
                          minimum=schema_dict.get("minimum"),
                          maximum=schema_dict.get("maximum"),
                          nullable=schema_dict.get("nullable", False),
                          default=schema_dict.get("default", UNDEFINED))

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
    def _parse_component_ref(cls, ref: str, comp_name: str) -> str:
        ref_parts = ref.split("/")
        if len(ref_parts) != 4 or ref_parts[0] != '#' or ref_parts[1] != 'components' or ref_parts[2] != comp_name:
            raise ValueError(f"invalid {comp_name} reference: {ref}")
        return ref_parts[3]

    def __init__(self,
                 version: str,
                 path_items: List[PathItem],
                 components: Components):
        assert_not_none_not_empty(version, name="version")
        assert_not_none(path_items, name="path_items")
        assert_not_none(components, name="components")
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
