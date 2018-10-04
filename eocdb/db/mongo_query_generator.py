from typing import Optional, List

from eocdb.core import QueryVisitor
from eocdb.core.query.query import FieldWildcardQuery, T, FieldRangeQuery, FieldValueQuery, UnaryOpQuery, BinaryOpQuery, \
    PhraseQuery


class MongoQueryGenerator(QueryVisitor[str]):

    def __init__(self):
        self.query_dict = {}
        self.last_field = None

    @property
    def query(self):
        if len(self.query_dict) == 0:
            return self.last_field

        return self.query_dict

    def visit_phrase(self, q: PhraseQuery, terms: List[T]) -> Optional[T]:
        raise NotImplementedError()

    def visit_binary_op(self, q: BinaryOpQuery, term1: T, term2: T) -> Optional[T]:
        if q.op == 'AND':
            self.query_dict.update({q.term1.name: q.term1.value, q.term2.name: q.term2.value})
        elif q.op == 'OR':
            self.query_dict.update({'$or': [{q.term1.name: q.term1.value}, {q.term2.name: q.term2.value}]})
        else:
            raise NotImplementedError()

        return self.query_dict

    def visit_unary_op(self, q: UnaryOpQuery, term: T) -> Optional[T]:
        raise NotImplementedError()

    def visit_field_value(self, q: FieldValueQuery) -> Optional[T]:
        self.last_field = {q.name : q.value}
        return self.last_field

    def visit_field_range(self, q: FieldRangeQuery) -> Optional[T]:
        self.query_dict.update({q.name : {'$gte' : q.start_value, '$lte': q.end_value}})
        return self.query_dict

    def visit_field_wildcard(self, q: FieldWildcardQuery) -> Optional[T]:
        if '?' in q.value:
            reg_exp = q.value.replace('?', '.')
        elif '*' in q.value:
            reg_exp = q.value.replace('*', '.*')
        else:
            raise NotImplementedError

        self.query_dict.update({q.name: {'$regex': reg_exp}})
        return self.query_dict