from typing import List, Tuple, Optional, Union, Type

from ocdb.core.query.query import Query, QueryBuilder, FieldValue, FieldQuery, \
    KW_AND, KW_OR, KW_NOT, KEYWORDS, OPERATORS, OP_INCLUDE, OP_EXCLUDE, FieldWildcardQuery

_OP_CHARS = ', '.join(f'[{op}]' for op in OPERATORS)


class QuerySyntaxError(Exception):
    def __init__(self, position: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = position


Token = Union[Tuple[str, str, int], Tuple[None, None, None]]

_NONE_TOKEN = (None, None, None)


class QueryParser:

    @classmethod
    def parse(cls, query: str, builder: Type[QueryBuilder] = QueryBuilder) -> Optional[Query]:
        return QueryParser(query, builder=builder)._parse(context_name=None)

    def __init__(self, query: str, builder: Type[QueryBuilder]):
        self._query = query
        self._builder = builder
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
        return self._builder.phrase(*terms)

    def _parse_or(self, context_name: str = None) -> Optional[Query]:
        term1 = self._parse_and(context_name=context_name)
        if term1 is None:
            return None
        token_type, token_value, token_pos = self._get_token()
        if token_type == QueryTokenizer.TOKEN_TYPE_KEYWORD and token_value == KW_OR:
            self._next_token()
            term2 = self._parse_or(context_name=context_name)
            if term2 is None:
                return term1
            return self._builder.OR(term1, term2)
        else:
            return term1

    def _parse_and(self, context_name: str = None) -> Optional[Query]:
        term1 = self._parse_unary(context_name=context_name)
        if term1 is None:
            return None
        token_type, token_value, token_pos = self._get_token()
        if token_type == QueryTokenizer.TOKEN_TYPE_KEYWORD and token_value == KW_AND:
            self._next_token()
            term2 = self._parse_and(context_name=context_name)
            if term2 is None:
                return term1
            return self._builder.AND(term1, term2)
        else:
            return term1

    def _parse_unary(self, context_name: str = None) -> Optional[Query]:
        token_type, token_value, token_pos = self._get_token()
        if token_type == QueryTokenizer.TOKEN_TYPE_KEYWORD and token_value == KW_NOT:
            self._next_token()
            term = self._parse_unary(context_name=context_name)
            if term is None:
                raise QuerySyntaxError(token_pos, f'Term missing after {KW_NOT}')
            return self._builder.NOT(term)
        elif token_type == QueryTokenizer.TOKEN_TYPE_CONTROL and token_value in OPERATORS:
            op = token_value
            self._next_token()
            term = self._parse_primary(context_name=context_name)
            if term is None:
                raise QuerySyntaxError(token_pos, f'Term missing after [{op}]')
            if not isinstance(term, FieldQuery):
                raise QuerySyntaxError(token_pos, f'Value or value range expected after [{op}]')
            if op == OP_INCLUDE:
                return self._builder.include(term)
            elif op == OP_EXCLUDE:
                return self._builder.exclude(term)
            else:
                assert False
        else:
            return self._parse_primary(context_name=context_name)

    def _parse_primary(self, context_name: str = None) -> Optional[Query]:
        token_type, token_value, token_pos = self._get_token()
        new_context_name = None
        if token_type == QueryTokenizer.TOKEN_TYPE_TEXT or token_type == QueryTokenizer.TOKEN_TYPE_QTEXT:
            self._next_token()
            value = token_value
            token_type, token_value, token_pos = self._get_token()
            if token_type == QueryTokenizer.TOKEN_TYPE_CONTROL and token_value == ':':
                self._next_token()
                new_context_name = value
            else:
                self._prev_token()

        token_type, token_value, token_pos = self._get_token()
        if self._is_value_token_type(token_type):
            is_text = token_type == QueryTokenizer.TOKEN_TYPE_TEXT
            self._next_token()
            if is_text and FieldWildcardQuery.is_wildcard_text(token_value):
                return self._builder.wildcard(token_value, name=new_context_name or context_name)
            else:
                return self._builder.value(token_value, name=new_context_name or context_name)

        if token_type == QueryTokenizer.TOKEN_TYPE_CONTROL and (token_value == '[' or token_value == '{'):
            range_open_char = token_value
            range_close_char = ']' if range_open_char == '[' else '}'
            is_exclusive = range_open_char == '{'
            self._next_token()
            token_type, token_value, token_pos = self._get_token()
            if self._is_value_token_type(token_type):
                start_value = token_value
                self._next_token()
                token_type, token_value, token_pos = self._get_token()
                if token_type == QueryTokenizer.TOKEN_TYPE_TEXT and token_value == 'TO':
                    self._next_token()
                    token_type, token_value, token_pos = self._get_token()
                    if self._is_value_token_type(token_type):
                        end_value = token_value
                        self._next_token()
                        token_type, token_value, token_pos = self._get_token()
                        if token_type != QueryTokenizer.TOKEN_TYPE_CONTROL or token_value != range_close_char:
                            raise QuerySyntaxError(token_pos, f'Missing [{range_close_char}] to close a value range')
                        self._next_token()
                        if is_exclusive:
                            return self._builder.within(start_value, end_value, name=new_context_name or context_name)
                        else:
                            return self._builder.inrange(start_value, end_value, name=new_context_name or context_name)
                    else:
                        raise QuerySyntaxError(token_pos, f'Unexpected [{token_value}] after "TO" in value range')
                else:
                    raise QuerySyntaxError(token_pos, f'Missing keyword "TO" after first value in value range')
            else:
                raise QuerySyntaxError(token_pos, f'Missing first value of value range after [${range_open_char}]')

        if token_type == QueryTokenizer.TOKEN_TYPE_CONTROL and token_value == '(':
            self._next_token()
            term = self._parse(new_context_name or context_name)
            token_type, token_value, token_pos = self._get_token()
            if token_type != QueryTokenizer.TOKEN_TYPE_CONTROL or token_value != ')':
                raise QuerySyntaxError(token_pos, f'Missing closing [)]')

            self._next_token()
            return term

        if new_context_name:
            raise QuerySyntaxError(token_pos, f'Missing value or value range after [{new_context_name}:]')

        if token_type == QueryTokenizer.TOKEN_TYPE_CONTROL and token_value == ')':
            # don't self._inc() here, it is done above in the '(' case
            return None

        return None

    @classmethod
    def _is_value_token_type(cls, token_type: int) -> bool:
        return token_type in QueryTokenizer.VALUE_TOKEN_TYPES

    def _get_token(self) -> Token:
        if self._index < self._size:
            return self._tokens[self._index]
        return _NONE_TOKEN

    def _next_token(self):
        self._index += 1

    def _prev_token(self):
        self._index -= 1


class QueryTokenizer:
    TOKEN_TYPE_CONTROL = 'CONTROL'
    TOKEN_TYPE_KEYWORD = 'KEYWORD'
    TOKEN_TYPE_TEXT = 'TEXT'
    TOKEN_TYPE_NUMBER = 'NUMBER'
    TOKEN_TYPE_QTEXT = 'QTEXT'

    VALUE_TOKEN_TYPES = {TOKEN_TYPE_TEXT,
                         TOKEN_TYPE_QTEXT,
                         TOKEN_TYPE_NUMBER}

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
                self._consume_literal_or_keyword(i1)
                break
            elif c.isspace():
                self._consume_literal_or_keyword(i1)
                i1 = self._eat_space()
            elif c == '\\':
                self._eat_char()
                self._eat_char()
            elif c == ':':
                self._consume_literal_or_keyword(i1)
                i1 = self._eat_ctrl_char_token(c)
            elif c == '[' or c == ']' or c == '{' or c == '}':
                self._consume_literal_or_keyword(i1)
                i1 = self._eat_ctrl_char_token(c)
            elif c == '(':
                self._consume_literal_or_keyword(i1)
                i1 = self._eat_ctrl_char_token(c)
                self._open_level()
            elif c == ')':
                self._consume_literal_or_keyword(i1)
                i1 = self._eat_ctrl_char_token(c)
                self._close_level()
            elif c == '"' or c == "'":
                self._consume_literal_or_keyword(i1)
                i1 = self._eat_quoted_text(c)
            else:
                self._eat_char()

        self._check_level_opened()

        return self._tokens

    def _consume_literal_or_keyword(self, start_index: int):
        end_index = self._index
        text = self._query[start_index: end_index]
        if text:
            if text in KEYWORDS:
                self._new_token(QueryTokenizer.TOKEN_TYPE_KEYWORD, text, start_index)
            elif text in OPERATORS:
                self._new_token(QueryTokenizer.TOKEN_TYPE_CONTROL, text, start_index)
            else:
                try:
                    value = int(text)
                    self._new_token(QueryTokenizer.TOKEN_TYPE_NUMBER, value, start_index)
                except ValueError:
                    try:
                        value = float(text)
                        self._new_token(QueryTokenizer.TOKEN_TYPE_NUMBER, value, start_index)
                    except ValueError:
                        i = 0
                        while i < len(text) and text[i] in OPERATORS:
                            self._new_token(QueryTokenizer.TOKEN_TYPE_CONTROL, text[i], start_index + i)
                            i += 1
                        self._new_token(QueryTokenizer.TOKEN_TYPE_TEXT, text[i:], start_index + i)

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

    def _new_token(self, typ: str, text: FieldValue, index: int):
        self._tokens.append((typ, text, index))

    def _open_level(self):
        self._level += 1

    def _close_level(self):
        self._level -= 1
        self._check_level_closed()

    def _check_level_closed(self):
        if self._level < 0:
            raise QuerySyntaxError(self._index, f'Missing matching [(]')

    def _check_level_opened(self):
        if self._level > 0:
            raise QuerySyntaxError(self._index, f'Missing matching [)]')
