from abc import ABCMeta, abstractmethod
from typing import List, Dict, Union

from ...core.asserts import *

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


class Schema(metaclass=ABCMeta):

    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @property
    @abstractmethod
    def format(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def items(self) -> Optional["Schema"]:
        pass

    @property
    @abstractmethod
    def properties(self) -> Optional[List[Property]]:
        pass

    @property
    @abstractmethod
    def ref_name(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def enum(self) -> Optional[Enum]:
        pass

    @property
    @abstractmethod
    def minimum(self) -> Optional[Number]:
        pass

    @property
    @abstractmethod
    def maximum(self) -> Optional[Number]:
        pass

    @property
    @abstractmethod
    def nullable(self) -> bool:
        pass

    @property
    @abstractmethod
    def default(self) -> Any:
        pass


class SchemaImpl(Schema):
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
    def __init__(self):
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

    @property
    def default(self) -> Any:
        return self.delegate.default


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
    def schemas(self) -> Dict[str, SchemaProxy]:
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

    @version.setter
    def version(self, value: str):
        self._version = value

    @property
    def path_items(self) -> List[PathItem]:
        return self._path_items

    @path_items.setter
    def path_items(self, value: List[PathItem]):
        self._path_items = value

    @property
    def components(self) -> Components:
        return self._components

    @components.setter
    def components(self, value: Components):
        self._components = value
