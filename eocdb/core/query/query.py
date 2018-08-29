from abc import ABCMeta, abstractmethod
from typing import List, Optional, Any, TypeVar, Generic, Union

KW_AND = 'AND'
KW_OR = 'OR'
KW_NOT = 'NOT'
KEYWORDS = {KW_AND, KW_OR, KW_NOT}

OP_INCLUDE = '+'
OP_EXCLUDE = '-'
OPERATORS = {OP_INCLUDE, OP_EXCLUDE}


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


class PhraseQuery(Query):
    def __init__(self, terms: List[Query]):
        self.terms = terms

    def __eq__(self, other) -> bool:
        return isinstance(other, PhraseQuery) and self.terms == other.terms

    def __str__(self) -> str:
        return ' '.join(map(str, self.terms))

    def __repr__(self) -> str:
        args = ', '.join(map(repr, self.terms))
        return f'PhraseQuery([{args}])'

    def accept(self, visitor: 'QueryVisitor') -> Any:
        return visitor.visit_phrase(self, [term.accept(visitor) for term in self.terms])

    def op_precedence(self) -> int:
        return 400


class BinaryOpQuery(Query):
    def __init__(self, op: str, term1: Query, term2: Query):
        self.op = op
        self.term1 = term1
        self.term2 = term2

    def __eq__(self, other):
        return isinstance(other, BinaryOpQuery) \
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

    def __repr__(self):
        t1 = repr(self.term1)
        t2 = repr(self.term2)
        return f'BinaryOpQuery("{self.op}", {t1}, {t2})'

    def accept(self, visitor: 'QueryVisitor') -> Any:
        return visitor.visit_binary_op(self, self.term1.accept(visitor), self.term2.accept(visitor))

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
        return isinstance(other, UnaryOpQuery) \
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

    def __repr__(self):
        return f'UnaryOpQuery("{self.op}", {repr(self.term)})'

    def accept(self, visitor: 'QueryVisitor') -> Any:
        return visitor.visit_unary_op(self, self.term.accept(visitor))

    def op_precedence(self) -> int:
        if self.op == KW_NOT:
            return 800
        else:
            return 900


class RangeQuery(Query):
    def __init__(self,
                 start_value: Union[str, float, int],
                 end_value: Union[str, float, int],
                 name: str = None,
                 is_exclusive=False):
        self.name = name  # If None, the context-specific default field name is used
        self.start_value = start_value
        self.end_value = end_value
        self.is_exclusive = is_exclusive

    def __eq__(self, other):
        return isinstance(other, TextQuery) \
               and self.name == other.name \
               and self.start_value == other.start_value \
               and self.end_value == other.end_value \
               and self.is_exclusive == other.is_exclusive

    def __str__(self) -> str:
        s = ''
        if self.name:
            s += self.name + ':' + s
        v = f'{self.start_value} TO {self.end_value}'
        if self.is_exclusive:
            s += '{' + v + '}'
        else:
            s += '[' + v + ']'
        return s

    def __repr__(self):
        args = f'{self.start_value}, {self.end_value}'
        if self.name:
            args += f', name="{self.name}"'
        if self.is_exclusive:
            args += f', is_exclusive={self.is_exclusive}'
        return f'RangeQuery({args})'

    def accept(self, visitor: 'QueryVisitor') -> Any:
        return visitor.visit_range(self)

    def op_precedence(self) -> int:
        return 1000


class TextQuery(Query):
    def __init__(self, text: str, name: str = None, is_quoted=False):
        self.name = name  # If None, the context-specific default field name is used
        self.text = text
        self.is_quoted = is_quoted

    @property
    def is_wildcard(self):
        return not self.is_quoted and ('*' in self.text or '?' in self.text)

    def __eq__(self, other):
        return isinstance(other, TextQuery) \
               and self.name == other.name \
               and self.text == other.text \
               and self.is_quoted == other.is_quoted

    def __str__(self) -> str:
        s = ''
        if self.name:
            s += self.name + ':'
        if self.is_quoted:
            s += f'"{self.text}"'
        else:
            s += self.text
        return s

    def __repr__(self):
        args = f'"{self.text}"'
        if self.name:
            args += f', name="{self.name}"'
        if self.is_quoted:
            args += f', is_quoted={self.is_quoted}'
        return f'TextQuery({args})'

    def accept(self, visitor: 'QueryVisitor') -> Any:
        return visitor.visit_text(self)

    def op_precedence(self) -> int:
        return 1000


T = TypeVar('T')


class QueryVisitor(Generic[T], metaclass=ABCMeta):
    """ Visitor used to visit all nodes of a Query tree. """

    @abstractmethod
    def visit_phrase(self, qt: PhraseQuery, terms: List[T]) -> Optional[T]:
        """
        Visit a PhraseQuery query term and compute an optional result.
        :param qt: The PhraseQuery query term to be visited.
        :param terms: The results of the list elements' visit.
        :return: The optional result of the visit.
        """

    @abstractmethod
    def visit_binary_op(self, qt: BinaryOpQuery, term1: T, term2: T) -> Optional[T]:
        """
        Visit a BinaryOpQuery query term and compute an optional result.
        :param qt: The BinaryOpQuery query term to be visited.
        :param term1: The result of the first operand's visit.
        :param term2: The result of the second operand's visit.
        :return: The optional result of the visit.
        """

    @abstractmethod
    def visit_unary_op(self, qt: UnaryOpQuery, term: T) -> Optional[T]:
        """
        Visit a UnaryOpQuery query term and compute an optional result.
        :param qt: The UnaryOpQuery query term to be visited.
        :param term: The result of the unary operand's visit.
        :return: The optional result of the visit.
        """

    @abstractmethod
    def visit_text(self, qt: TextQuery) -> Optional[T]:
        """
        Visit a TextQuery query term and compute an optional result.
        :param qt: The TextQuery query term to be visited.
        :return: The optional result of the visit.
        """

    @abstractmethod
    def visit_range(self, qt: RangeQuery) -> Optional[T]:
        """
        Visit a RangeQuery query term and compute an optional result.
        :param qt: The RangeQuery query term to be visited.
        :return: The optional result of the visit.
        """
