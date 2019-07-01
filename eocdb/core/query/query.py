from abc import ABCMeta, abstractmethod
from typing import List, Optional, Any, TypeVar, Generic, Union, Sequence

KW_AND = 'AND'
KW_OR = 'OR'
KW_NOT = 'NOT'
KEYWORDS = {KW_AND, KW_OR, KW_NOT}

OP_INCLUDE = '+'
OP_EXCLUDE = '-'
OPERATORS = {OP_INCLUDE, OP_EXCLUDE}

_NoneType = type(None)

FIELD_VALUE_TYPES = {str, int, float, _NoneType}

FieldValue = Union[str, int, float, None]


class Query(metaclass=ABCMeta):
    """
    Interface to be implemented by all query terms.

    * QTList - same as
    """

    @abstractmethod
    def accept(self, visitor: 'QueryVisitor') -> Any:
        pass

    @abstractmethod
    def op_precedence(self) -> int:
        return False

    def is_of_same_type(self, other: Any):
        return type(self) is type(other)

    @abstractmethod
    def args_to_repr(self) -> str:
        """ Get Python representation of constructor args."""

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.args_to_repr()})'


class PhraseQuery(Query):
    def __init__(self, terms: Sequence[Query]):
        self.terms = tuple(terms)

    def __eq__(self, other) -> bool:
        return self.is_of_same_type(other) and self.terms == other.terms

    def __str__(self) -> str:
        return ' '.join(map(str, self.terms))

    def args_to_repr(self) -> str:
        args = ', '.join(map(repr, self.terms))
        return f'[{args}]'

    def accept(self, visitor: 'QueryVisitor') -> Any:
        lst = []
        for term in self.terms:
            if isinstance(term, UnaryOpQuery):
                lst.append(visitor.visit_unary_op(q=term, term=term.term))
            elif isinstance(term, FieldValueQuery):
                lst.append(str(term.value))
            else:
                lst.append(str(term))

        return visitor.visit_phrase(self, lst)

    def op_precedence(self) -> int:
        return 400


class BinaryOpQuery(Query):
    def __init__(self, op: str, term1: Query, term2: Query):
        self.op = op
        self.term1 = term1
        self.term2 = term2

    def __eq__(self, other):
        return self.is_of_same_type(other) \
               and self.op == other.op \
               and self.term1 == other.term1 \
               and self.term2 == other.term2

    def __str__(self) -> str:
        t1 = str(self.term1)
        t2 = str(self.term2)
        if self.op_precedence() > self.term1.op_precedence():
            t1 = f'({t1})'
        if self.op_precedence() > self.term2.op_precedence():
            t2 = f'({t2})'
        return f'{t1} {self.op} {t2}'

    def args_to_repr(self) -> str:
        t1 = repr(self.term1)
        t2 = repr(self.term2)
        return f'"{self.op}", {t1}, {t2}'

    def accept(self, visitor: 'QueryVisitor') -> Any:
        term1 = self.term1.accept(visitor)
        term2 = self.term2.accept(visitor)
        return visitor.visit_binary_op(self, term1, term2)

    def op_precedence(self) -> int:
        if self.op == KW_OR:
            return 500
        else:
            return 600


class UnaryOpQuery(Query):
    def __init__(self, op: str, term: Query):
        self.op = op
        self.term = term

    def __eq__(self, other) -> bool:
        return self.is_of_same_type(other) \
               and self.op == other.op \
               and self.term == other.term

    def __str__(self) -> str:
        term = str(self.term)
        if self.op_precedence() > self.term.op_precedence():
            term = f'({term})'
        if self.op in KEYWORDS:
            return f'{self.op} {term}'
        else:
            return f'{self.op}{term}'

    def args_to_repr(self) -> str:
        return f'"{self.op}", {repr(self.term)}'

    def accept(self, visitor: 'QueryVisitor') -> Any:
        return visitor.visit_unary_op(self, self.term.accept(visitor))

    def op_precedence(self) -> int:
        if self.op == KW_NOT:
            return 800
        else:
            return 900


class FieldQuery(Query, metaclass=ABCMeta):
    def __init__(self, name: Optional[str]):
        self.name = name

    def op_precedence(self) -> int:
        return 1000

    @abstractmethod
    def value_to_str(self):
        """ Turn value into string. """

    def __str__(self) -> str:
        value = self.value_to_str()
        return f'{self.name}:{value}' if self.name else value

    @abstractmethod
    def value_args_to_repr(self):
        """ Turn value(s) into Python representation. """

    def args_to_repr(self) -> str:
        args = self.value_args_to_repr()
        return f'"{self.name}", {args}' if self.name else f'None, {args}'


class FieldValueQuery(FieldQuery):
    @classmethod
    def is_text(cls, value: FieldValue):
        return isinstance(value, str)

    def __init__(self, name: Optional[str], value: FieldValue):
        super().__init__(name)
        assert type(value) in FIELD_VALUE_TYPES
        self.value = value

    def __eq__(self, other):
        return self.is_of_same_type(other) \
               and self.name == other.name \
               and self.value == other.value

    def value_to_str(self):
        return '"' + self.value.replace('"', '\\"') + '"' \
            if self._is_quoted_text() else str(self.value)

    def value_args_to_repr(self):
        return '"' + self.value.replace('"', '\\"') + '"' \
            if isinstance(self.value, str) else repr(self.value)

    def accept(self, visitor: 'QueryVisitor') -> Any:
        return visitor.visit_field_value(self)

    def op_precedence(self) -> int:
        return 1000

    def _is_text(self):
        return self.is_text(self.value)

    def _is_quoted_text(self) -> bool:
        return self._is_text() \
               and any(map(lambda c: c in ' +-&|!(){}[]^"~*?:\\', self.value))


class FieldWildcardQuery(FieldValueQuery):

    @classmethod
    def is_wildcard_text(cls, value: FieldValue) -> bool:

        if not cls.is_text(value):
            return False

        escape = False
        wildcard_char_seen = False
        for i in range(len(value)):
            c = value[i]
            if c == '\\':
                escape = True
            elif not escape and c == '?' or c == '*':
                wildcard_char_seen = True
            elif not escape and c.isspace():
                return False
            else:
                escape = False

        return wildcard_char_seen

    def __init__(self, name: Optional[str], value: str):
        super().__init__(name, value)
        assert isinstance(value, str)

    def accept(self, visitor: 'QueryVisitor') -> Any:
        return visitor.visit_field_wildcard(self)

    def _is_quoted_text(self) -> bool:
        return False


class FieldRangeQuery(FieldQuery):

    def __init__(self, name: Optional[str], start_value: FieldValue, end_value: FieldValue, is_exclusive=False):
        super().__init__(name)
        assert not (start_value is None and end_value is None)
        assert type(start_value) in FIELD_VALUE_TYPES
        assert type(end_value) in FIELD_VALUE_TYPES
        if start_value is not None and end_value is not None:
            if isinstance(start_value, str) or isinstance(end_value, str):
                start_value = str(start_value)
                end_value = str(end_value)
            elif isinstance(start_value, float) or isinstance(end_value, float):
                start_value = float(start_value)
                end_value = float(end_value)
            elif isinstance(start_value, int) or isinstance(end_value, int):
                start_value = int(start_value)
                end_value = int(end_value)
        self.start_value = start_value
        self.end_value = end_value
        self.is_exclusive = is_exclusive

    def __eq__(self, other):
        return self.is_of_same_type(other) \
               and self.name == other.name \
               and self.start_value == other.start_value \
               and self.end_value == other.end_value \
               and self.is_exclusive == other.is_exclusive

    def value_to_str(self):
        v = f'{self.start_value} TO {self.end_value}'
        if self.is_exclusive:
            v = '{' + v + '}'
        else:
            v = '[' + v + ']'
        return v

    def value_args_to_repr(self):
        args = f'{self.start_value}, {self.end_value}'
        if self.is_exclusive:
            args += f', is_exclusive={self.is_exclusive}'
        return args

    def accept(self, visitor: 'QueryVisitor') -> Any:
        return visitor.visit_field_range(self)


T = TypeVar('T')


class QueryVisitor(Generic[T], metaclass=ABCMeta):
    """ Visitor used to visit all nodes of a Query tree. """

    @abstractmethod
    def visit_phrase(self, q: PhraseQuery, terms: List[T]) -> Optional[T]:
        """
        Visit a PhraseQuery query term and compute an optional result.
        :param q: The PhraseQuery query term to be visited.
        :param terms: The results of the list elements' visit.
        :return: The optional result of the visit.
        """

    @abstractmethod
    def visit_binary_op(self, q: BinaryOpQuery, term1: T, term2: T) -> Optional[T]:
        """
        Visit a BinaryOpQuery query term and compute an optional result.
        :param q: The BinaryOpQuery query term to be visited.
        :param term1: The result of the first operand's visit.
        :param term2: The result of the second operand's visit.
        :return: The optional result of the visit.
        """

    @abstractmethod
    def visit_unary_op(self, q: UnaryOpQuery, term: T) -> Optional[T]:
        """
        Visit a UnaryOpQuery query term and compute an optional result.
        :param q: The UnaryOpQuery query term to be visited.
        :param term: The result of the unary operand's visit.
        :return: The optional result of the visit.
        """

    @abstractmethod
    def visit_field_value(self, q: FieldValueQuery) -> Optional[T]:
        """
        Visit a FieldValueQuery query term and compute an optional result.
        :param q: The FieldValueQuery query term to be visited.
        :return: The optional result of the visit.
        """

    @abstractmethod
    def visit_field_range(self, q: FieldRangeQuery) -> Optional[T]:
        """
        Visit a FieldRangeQuery query term and compute an optional result.
        :param q: The FieldRangeQuery query term to be visited.
        :return: The optional result of the visit.
        """

    @abstractmethod
    def visit_field_wildcard(self, q: FieldWildcardQuery) -> Optional[T]:
        """
        Visit a FieldRangeQuery query term and compute an optional result.
        :param q: The FieldRangeQuery query term to be visited.
        :return: The optional result of the visit.
        """


# noinspection PyPep8Naming
class QueryBuilder:

    @classmethod
    def value(cls, v: FieldValue, name: str = None):
        return FieldValueQuery(name, v)

    @classmethod
    def wildcard(cls, v: str, name: str = None):
        return FieldWildcardQuery(name, v)

    @classmethod
    def inrange(cls, v1: FieldValue, v2: FieldValue, name: str = None):
        return FieldRangeQuery(name, v1, v2, is_exclusive=False)

    @classmethod
    def within(cls, v1: FieldValue, v2: FieldValue, name: str = None):
        return FieldRangeQuery(name, v1, v2, is_exclusive=True)

    @classmethod
    def include(cls, q: FieldQuery):
        return UnaryOpQuery('+', q)

    @classmethod
    def exclude(cls, q: FieldQuery):
        return UnaryOpQuery('-', q)

    @classmethod
    def phrase(cls, *terms: Query):
        return PhraseQuery(terms)

    @classmethod
    def NOT(cls, q: Query):
        return UnaryOpQuery('NOT', q)

    @classmethod
    def AND(cls, q1: Query, q2: Query):
        return BinaryOpQuery('AND', q1, q2)

    @classmethod
    def OR(cls, q1: Query, q2: Query):
        return BinaryOpQuery('OR', q1, q2)
