from typing import List, Tuple, Optional

from eocdb.core.query.query import Query, PhraseQuery, UnaryOpQuery, BinaryOpQuery, TextQuery, \
    KW_AND, KW_OR, KW_NOT, KEYWORDS, OPERATORS

_OP_CHARS = ', '.join(f'[{op}]' for op in OPERATORS)


class QuerySyntaxError(Exception):
    def __init__(self, position: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = position


Token = Tuple[str, str, int]


class QueryParser:

    @classmethod
    def parse(cls, query: str) -> Optional[Query]:
        return QueryParser(query)._parse(context_name=None)

    def __init__(self, query: str):
        self._query = query
        self._tokens = QueryTokenizer.tokenize(self._query)
        self._size = len(self._tokens)
        self._index = 0

    def _parse(self, context_name: str = None) -> Optional[Query]:
        return self._parse_list(context_name=context_name)

    def _parse_list(self, context_name: str = None) -> Optional[Query]:
        terms = []
        while True:
            term = self._parse_or(context_name=context_name)
            if term is None:
                break
            terms.append(term)
        if len(terms) == 0:
            return None
        if len(terms) == 1:
            return terms[0]
        return PhraseQuery(terms)

    def _parse_or(self, context_name: str = None) -> Optional[Query]:
        term1 = self._parse_and(context_name=context_name)
        if term1 is None:
            return None
        token_type, token_value, token_pos = self._peek()
        if token_type == QueryTokenizer.TOKEN_TYPE_KEYWORD and token_value == KW_OR:
            self._inc()
            term2 = self._parse_or(context_name=context_name)
            if term2 is None:
                return term1
            return BinaryOpQuery(token_value, term1, term2)
        else:
            return term1

    def _parse_and(self, context_name: str = None) -> Optional[Query]:
        term1 = self._parse_unary(context_name=context_name)
        if term1 is None:
            return None
        token_type, token_value, token_pos = self._peek()
        if token_type == QueryTokenizer.TOKEN_TYPE_KEYWORD and token_value == KW_AND:
            self._inc()
            term2 = self._parse_and(context_name=context_name)
            if term2 is None:
                return term1
            return BinaryOpQuery(token_value, term1, term2)
        else:
            return term1

    def _parse_unary(self, context_name: str = None) -> Optional[Query]:
        token_type, token_value, token_pos = self._peek()
        if token_type == QueryTokenizer.TOKEN_TYPE_KEYWORD and token_value == KW_NOT:
            self._inc()
            term = self._parse_unary(context_name=context_name)
            if term is None:
                raise QuerySyntaxError(token_pos, f'Term missing after {KW_NOT}')
            return UnaryOpQuery(KW_NOT, term)
        elif token_type == QueryTokenizer.TOKEN_TYPE_CONTROL and token_value in OPERATORS:
            self._inc()
            term = self._parse_primary(context_name=context_name)
            if term is None:
                raise QuerySyntaxError(token_pos, f'Term missing after [{token_value}]')
            return UnaryOpQuery(token_value, term)
        else:
            return self._parse_primary(context_name=context_name)

    def _parse_primary(self, context_name: str = None) -> Optional[Query]:
        token_type, token_value, token_pos = self._peek()
        is_text = token_type == QueryTokenizer.TOKEN_TYPE_TEXT
        is_qtext = token_type == QueryTokenizer.TOKEN_TYPE_QTEXT
        if is_text or is_qtext:
            self._inc()
            text = token_value
            token_type, token_value, token_pos = self._peek()
            if token_type == QueryTokenizer.TOKEN_TYPE_CONTROL and token_value == ':':
                self._inc()
                name = text
                if not name.isidentifier():
                    raise QuerySyntaxError(token_pos, 'Name expected before [:]')
                token_type, text, token_pos = self._peek()
                is_text = token_type == QueryTokenizer.TOKEN_TYPE_TEXT
                is_qtext = token_type == QueryTokenizer.TOKEN_TYPE_QTEXT
                if is_text or is_qtext:
                    self._inc()
                    return TextQuery(text, name=name, is_quoted=is_qtext)
                raise QuerySyntaxError(token_pos, 'Missing text after [:]')
            else:
                return TextQuery(text, name=context_name, is_quoted=is_qtext)

        if token_type == QueryTokenizer.TOKEN_TYPE_CONTROL and token_value == '(':
            self._inc()
            term = self._parse(context_name)
            token_type, token_value, token_pos = self._peek()
            assert token_type == QueryTokenizer.TOKEN_TYPE_CONTROL and token_value == ')'
            self._inc()
            return term

        if token_type is not None:
            raise QuerySyntaxError(token_pos, f'Unexpected [{token_value}]')

        return None

    def _inc(self):
        self._index += 1

    def _push_back(self):
        self._index -= 1

    def _peek(self) -> Token:
        if self._index < self._size:
            return self._tokens[self._index]
        # noinspection PyTypeChecker
        return None, None, None


class QueryTokenizer:
    TOKEN_TYPE_CONTROL = 'CONTROL'
    TOKEN_TYPE_KEYWORD = 'KEYWORD'
    TOKEN_TYPE_TEXT = 'TEXT'
    TOKEN_TYPE_QTEXT = 'QTEXT'

    @classmethod
    def tokenize(cls, query: str) -> List[Token]:
        return QueryTokenizer(query)._tokenize()

    def __init__(self, query: str):
        self._query = query
        self._size = len(query)
        self._index = 0
        self._tokens = []
        self._level = 0

    def _tokenize(self) -> List[Token]:
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

    def _consume_text_or_keyword(self, start_index: int):
        end_index = self._index
        text = self._query[start_index: end_index]
        if text:
            if text in KEYWORDS:
                self._new_token(QueryTokenizer.TOKEN_TYPE_KEYWORD, text, start_index)
            else:
                self._new_token(QueryTokenizer.TOKEN_TYPE_TEXT, text, start_index)

    def _eat_ctrl_char_token(self, ctrl_char) -> int:
        start_index = self._index
        self._eat_char()
        self._new_token(QueryTokenizer.TOKEN_TYPE_CONTROL, ctrl_char, start_index)
        return self._index

    def _eat_quoted_text(self, quote_char: str) -> int:
        self._eat_char()
        start_index = self._index
        while self._peek() and self._peek() != quote_char:
            self._eat_char()
        if not self._peek():
            raise QuerySyntaxError(self._index, f'Missing matching [{quote_char}]')
        self._new_token(QueryTokenizer.TOKEN_TYPE_QTEXT, self._query[start_index: self._index], start_index)
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

    def _new_token(self, typ: str, text: str, index: int):
        self._tokens.append((typ, text, index))

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
