from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Optional, Any, TypeVar, Generic

KW_AND = 'AND'
KW_OR = 'OR'
KW_NOT = 'NOT'
KEYWORDS = {KW_AND, KW_OR, KW_NOT}

OP_INCLUDE = '+'
OP_EXCLUDE = '-'
OPERATORS = {OP_INCLUDE, OP_EXCLUDE}

_OP_CHARS = ', '.join(f'[{op}]' for op in OPERATORS)


class QuerySyntaxError(Exception):
    def __init__(self, position: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = position


class AbstractQT(metaclass=ABCMeta):
    """
    Interface to be implemented by all query terms.

    * QTList - same as
    """

    @abstractmethod
    def accept(self, visitor: 'QTVisitor') -> Any:
        pass

    @abstractmethod
    def op_precedence(self) -> int:
        return False


class QTList(AbstractQT):
    def __init__(self, terms: List[AbstractQT]):
        self.terms = terms

    def __eq__(self, other) -> bool:
        return isinstance(other, QTList) and self.terms == other.terms

    def __str__(self) -> str:
        return ' '.join(map(str, self.terms))

    def __repr__(self) -> str:
        args = ', '.join(map(repr, self.terms))
        return f'QTList([{args}])'

    def accept(self, visitor: 'QTVisitor') -> Any:
        return visitor.visit_list(self, [term.accept(visitor) for term in self.terms])

    def op_precedence(self) -> int:
        return 500


class QTBinOp(AbstractQT):
    def __init__(self, op: str, term1: AbstractQT, term2: AbstractQT):
        self.op = op
        self.term1 = term1
        self.term2 = term2

    def __eq__(self, other):
        return isinstance(other, QTBinOp) \
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
        return f'QTBinOp("{self.op}", {t1}, {t2})'

    def accept(self, visitor: 'QTVisitor') -> Any:
        return visitor.visit_binary_op(self, self.term1.accept(visitor), self.term2.accept(visitor))

    def op_precedence(self) -> int:
        if self.op == KW_OR:
            return 500
        else:
            return 600


class QTUnOp(AbstractQT):
    def __init__(self, op: str, term: AbstractQT):
        self.op = op
        self.term = term

    def __eq__(self, other) -> bool:
        return isinstance(other, QTUnOp) \
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
        return f'QTUnOp("{self.op}", {repr(self.term)})'

    def accept(self, visitor: 'QTVisitor') -> Any:
        return visitor.visit_unary_op(self, self.term.accept(visitor))

    def op_precedence(self) -> int:
        if self.op == KW_NOT:
            return 800
        else:
            return 900


class QTText(AbstractQT):
    def __init__(self, text: str, name: str = None, is_exact: bool = False, is_wildcard: bool = False):
        self.text = text
        self.name = name  # If None --> global search
        self.is_exact = is_exact
        self.is_wildcard = is_wildcard

    def __eq__(self, other):
        return isinstance(other, QTText) \
               and self.name == other.name \
               and self.text == other.text \
               and self.is_exact == other.is_exact \
               and self.is_wildcard == other.is_wildcard

    def __str__(self) -> str:
        s = ''
        if self.name:
            s += self.name + ':'
        if self.is_exact:
            s += f'"{self.text}"'
        else:
            s += self.text
        return s

    def __repr__(self):
        args = f'"{self.text}"'
        if self.name:
            args += f', name="{self.name}"'
        if self.is_exact:
            args += f', is_exact=True'
        if self.is_wildcard:
            args += f', is_wildcard=True'
        return f'QTText({args})'

    def accept(self, visitor: 'QTVisitor') -> Any:
        return visitor.visit_text(self)

    def op_precedence(self) -> int:
        return 1000


T = TypeVar('T')


class QTVisitor(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def visit_list(self, qt: QTList, terms: List[T]) -> Optional[T]:
        """
        Visit a QTList query term and compute an optional result.
        :param qt: The QTList query term to be visited.
        :param terms: The results of the list elements' visit.
        :return: The optional result of the visit.
        """

    @abstractmethod
    def visit_binary_op(self, qt: QTBinOp, term1: T, term2: T) -> Optional[T]:
        """
        Visit a QTBinOp query term and compute an optional result.
        :param qt: The QTBinOp query term to be visited.
        :param term1: The result of the first operand's visit.
        :param term2: The result of the second operand's visit.
        :return: The optional result of the visit.
        """

    @abstractmethod
    def visit_unary_op(self, qt: QTUnOp, term: T) -> Optional[T]:
        """
        Visit a QTUnOp query term and compute an optional result.
        :param qt: The QTUnOp query term to be visited.
        :param term: The result of the unary operand's visit.
        :return: The optional result of the visit.
        """

    @abstractmethod
    def visit_text(self, qt: QTText) -> Optional[T]:
        """
        Visit a QTText query term and compute an optional result.
        :param qt: The QTText query term to be visited.
        :return: The optional result of the visit.
        """


class QueryParser:

    @classmethod
    def parse(cls, query: str) -> Optional[AbstractQT]:
        return QueryParser(query)._parse_list()

    def __init__(self, query: str):
        self._query = query
        self._tokens = QueryTokenizer.tokenize(self._query)
        self._size = len(self._tokens)
        self._index = 0

    def _parse_list(self) -> Optional[AbstractQT]:
        terms = []
        while True:
            term = self._parse_or()
            if term is None:
                break
            terms.append(term)
        if len(terms) == 0:
            return None
        if len(terms) == 1:
            return terms[0]
        return QTList(terms)

    def _parse_or(self) -> Optional[AbstractQT]:
        term1 = self._parse_and()
        if term1 is None:
            return None
        t, v = self._peek()
        if t == QueryTokenizer.TOKEN_TYPE_KEYWORD and v == KW_OR:
            self._inc()
            term2 = self._parse_or()
            if term2 is None:
                return term1
            return QTBinOp(v, term1, term2)
        else:
            return term1

    def _parse_and(self) -> Optional[AbstractQT]:
        term1 = self._parse_unary()
        if term1 is None:
            return None
        t, v = self._peek()
        if t == QueryTokenizer.TOKEN_TYPE_KEYWORD and v == KW_AND:
            self._inc()
            term2 = self._parse_or()
            if term2 is None:
                return term1
            return QTBinOp(v, term1, term2)
        else:
            return term1

    def _parse_unary(self) -> Optional[AbstractQT]:
        t, v = self._peek()
        if t == QueryTokenizer.TOKEN_TYPE_KEYWORD and v == KW_NOT:
            self._inc()
            term = self._parse_unary()
            if term is None:
                raise QuerySyntaxError(0, f'Term missing after {KW_NOT}')
            return QTUnOp(KW_NOT, term)
        elif t == QueryTokenizer.TOKEN_TYPE_CONTROL and v in OPERATORS:
            self._inc()
            term = self._parse_primary()
            if term is None:
                raise QuerySyntaxError(0, f'Term missing after [{v}]')
            return QTUnOp(v, term)
        else:
            return self._parse_primary()

    def _parse_primary(self) -> Optional[AbstractQT]:
        t, v = self._peek()
        if t == QueryTokenizer.TOKEN_TYPE_CONTROL and v == '(':
            self._inc()
            term = self._parse_list()
            t, v = self._peek()
            assert t == QueryTokenizer.TOKEN_TYPE_CONTROL and v == ')'
            self._inc()
            return term
        if t == QueryTokenizer.TOKEN_TYPE_QUOTED_TEXT:
            self._inc()
            return QTText(v, is_exact=True)
        if t == QueryTokenizer.TOKEN_TYPE_WILDCARD_TEXT:
            self._inc()
            return QTText(v, is_wildcard=True)
        if t == QueryTokenizer.TOKEN_TYPE_TEXT:
            self._inc()
            text = v
            t, v = self._peek()
            if t == QueryTokenizer.TOKEN_TYPE_CONTROL and v == ':':
                self._inc()
                name = text
                if not name.isidentifier():
                    raise QuerySyntaxError(0, 'Name expected before [:]')
                t, text = self._peek()
                if t == QueryTokenizer.TOKEN_TYPE_TEXT:
                    self._inc()
                    return QTText(text, name=name)
                if t == QueryTokenizer.TOKEN_TYPE_QUOTED_TEXT:
                    self._inc()
                    return QTText(text, name=name, is_exact=True)
                if t == QueryTokenizer.TOKEN_TYPE_WILDCARD_TEXT:
                    self._inc()
                    return QTText(text, name=name, is_wildcard=True)
                raise QuerySyntaxError(0, 'Missing text after [:]')
            else:
                return QTText(text)
        if t is not None:
            raise QuerySyntaxError(0, f'Unexpected [{v}]')
        return None

    def _inc(self):
        self._index += 1

    def _push_back(self):
        self._index -= 1

    def _peek(self):
        if self._index < self._size:
            return self._tokens[self._index]
        return None, None


class QueryTokenizer:
    TOKEN_TYPE_CONTROL = 'CONTROL'
    TOKEN_TYPE_KEYWORD = 'KEYWORD'
    TOKEN_TYPE_TEXT = 'TEXT'
    TOKEN_TYPE_WILDCARD_TEXT = 'WILDCARD_TEXT'
    TOKEN_TYPE_QUOTED_TEXT = 'QUOTED_TEXT'

    @classmethod
    def tokenize(cls, query: str) -> List[Tuple[str, str]]:
        return QueryTokenizer(query)._tokenize()

    def __init__(self, query: str):
        self._query = query
        self._size = len(query)
        self._index = 0
        self._tokens = []
        self._level = 0

    def _tokenize(self):
        i1 = self._eat_space()
        while True:
            c = self._peek()
            if c == '':
                self._consume_text_or_keyword(i1)
                break
            elif c.isspace():
                self._consume_text_or_keyword(i1)
                i1 = self._eat_space()
            elif c == '\\':
                self._eat_char()
                self._eat_char()
            elif c in OPERATORS or c == ':':
                self._consume_text_or_keyword(i1)
                i1 = self._eat_ctrl_char_token(c)
            elif c == '(':
                self._consume_text_or_keyword(i1)
                i1 = self._eat_ctrl_char_token('(')
                self._open_level()
            elif c == ')':
                self._consume_text_or_keyword(i1)
                i1 = self._eat_ctrl_char_token(')')
                self._close_level()
            elif c == '"' or c == "'":
                self._consume_text_or_keyword(i1)
                i1 = self._eat_quoted_text(c)
            else:
                self._eat_char()

        self._check_level()

        return self._tokens

    def _consume_text_or_keyword(self, i1: int):
        i2 = self._index
        text = self._query[i1: i2]
        if text:
            text = text.replace('\\', '')
            if text in KEYWORDS:
                self._new_token(QueryTokenizer.TOKEN_TYPE_KEYWORD, text)
            elif '*' in text or '?' in text:
                self._new_token(QueryTokenizer.TOKEN_TYPE_WILDCARD_TEXT, text)
            else:
                self._new_token(QueryTokenizer.TOKEN_TYPE_TEXT, text)

    def _eat_ctrl_char_token(self, ctrl_char) -> int:
        self._eat_char()
        self._new_token(QueryTokenizer.TOKEN_TYPE_CONTROL, ctrl_char)
        return self._index

    def _eat_quoted_text(self, quote_char: str) -> int:
        self._eat_char()
        i1 = self._index
        while self._peek() and self._peek() != quote_char:
            self._eat_char()
        if not self._peek():
            raise QuerySyntaxError(self._index, f'Missing matching [{quote_char}]')
        self._new_token(QueryTokenizer.TOKEN_TYPE_QUOTED_TEXT, self._query[i1: self._index])
        self._eat_char()
        return self._index

    def _eat_space(self) -> int:
        while self._peek().isspace():
            self._eat_char()
        return self._index

    def _eat_char(self):
        self._index += 1
        return self._index

    def _peek(self) -> str:
        if self._index < self._size:
            return self._query[self._index]
        return ''

    def _new_token(self, typ: str, text: str):
        self._tokens.append((typ, text))

    def _open_level(self):
        self._level += 1

    def _close_level(self):
        self._level -= 1
        self._check_level()

    def _check_level(self):
        if self._level < 0:
            raise QuerySyntaxError(self._index, f'Missing matching [(]')
        if self._level > 0:
            raise QuerySyntaxError(self._index, f'Missing matching [)]')
