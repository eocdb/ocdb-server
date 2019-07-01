from typing import Optional, List

from eocdb.core import QueryVisitor
from eocdb.core.query.query import FieldWildcardQuery, T, FieldRangeQuery, FieldValueQuery, UnaryOpQuery, BinaryOpQuery, \
    PhraseQuery


class MongoQueryGenerator(QueryVisitor[str]):
    plain_fields = ["path", "submission_id", "status", "pgroup", "pname"]
    METADATA = 'metadata.'

    def __init__(self):
        self.query_dict = {}
        self.last_field = None

    @property
    def query(self):
        if len(self.query_dict) == 0:
            return self.last_field

        return self.query_dict

    def visit_phrase(self, q: PhraseQuery, terms: List[T]) -> Optional[T]:
        phrase = ' '.join(terms)
        query_dict = {'$text': {'$search': phrase}}
        self.query_dict.update(query_dict)
        return self.query_dict

    def visit_binary_op(self, q: BinaryOpQuery, term1: T, term2: T) -> Optional[T]:
        if q.op == 'AND':
            self.query_dict.update({'$and': [term1, term2]})
        elif q.op == 'OR':
            self.query_dict.update({'$or': [term1, term2]})
        else:
            raise NotImplementedError()

        return self.query_dict

    def visit_unary_op(self, q: UnaryOpQuery, term: T) -> Optional[T]:
        raise NotImplementedError()
        # if q.op == '+':
        #     self.query_dict.update({'$text': {'$search': '+' + q.term.value}})
        # elif q.op == '-':
        #     self.query_dict.update({'$text': {'$search': '-' + q.term.value}})
        # elif q.op == 'NOT':
        #     self.query_dict.update({'$not': q.term.value})
        # else:
        #     raise NotImplementedError()

        # return self.query_dict

    def visit_field_value(self, q: FieldValueQuery) -> Optional[T]:
        if q.name is None:
            return self.query_dict.update({'$text': {'$search': q.value}})

        name = self._get_db_field_name(q.name)
        self.last_field = {name: q.value}

        return self.last_field

    def visit_field_range(self, q: FieldRangeQuery) -> Optional[T]:
        name = self._get_db_field_name(q.name)
        self.query_dict.update({name: {'$gte': q.start_value, '$lte': q.end_value}})
        return self.query_dict

    def visit_field_wildcard(self, q: FieldWildcardQuery) -> Optional[T]:
        if '?' in q.value:
            reg_exp = q.value.replace('?', '.')
        elif '*' in q.value:
            reg_exp = q.value.replace('*', '.*')
        else:
            raise NotImplementedError

        name = self._get_db_field_name(q.name)

        #return {name: {'$regex': reg_exp}}
        self.query_dict.update({name: {'$regex': reg_exp}})
        return self.query_dict

    def _get_db_field_name(self, name: str) -> str:
        if name in self.plain_fields:
            return name

        return self.METADATA + name
