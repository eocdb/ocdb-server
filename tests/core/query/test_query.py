from typing import Optional, List
from unittest import TestCase

from eocdb.core.query.query import FieldValueQuery, PhraseQuery, UnaryOpQuery, BinaryOpQuery, QueryVisitor, \
    FieldRangeQuery, FieldWildcardQuery


class QueryTest(TestCase):
    def _assert_str_and_repr(self, expected_str, expected_repr, term):
        self.assertEqual(expected_str, str(term))
        self.assertEqual(expected_repr, repr(term))

    def test_field_value(self):
        self._assert_str_and_repr('cat',
                                  'FieldValueQuery(None, "cat")',
                                  FieldValueQuery(None, 'cat'))
        self._assert_str_and_repr('animal:cat',
                                  'FieldValueQuery("animal", "cat")',
                                  FieldValueQuery('animal', 'cat'))
        self._assert_str_and_repr('size:627247',
                                  'FieldValueQuery("size", 627247)',
                                  FieldValueQuery('size', 627247))
        self._assert_str_and_repr('"c*t"',
                                  'FieldValueQuery(None, "c*t")',
                                  FieldValueQuery(None, 'c*t'))
        self._assert_str_and_repr('animal:"cat dog"',
                                  'FieldValueQuery("animal", "cat dog")',
                                  FieldValueQuery('animal', 'cat dog'))

        self.assertEqual(1000, FieldValueQuery(None, 'cat').op_precedence())

        with self.assertRaises(AssertionError):
            FieldValueQuery('large', True)
        with self.assertRaises(AssertionError):
            FieldValueQuery('items', [1, 2])

    def test_field_wildcard(self):
        self._assert_str_and_repr('cat',
                                  'FieldWildcardQuery(None, "cat")',
                                  FieldWildcardQuery(None, 'cat'))
        self._assert_str_and_repr('animal:?at',
                                  'FieldWildcardQuery("animal", "?at")',
                                  FieldWildcardQuery('animal', '?at'))
        self._assert_str_and_repr('c*t',
                                  'FieldWildcardQuery(None, "c*t")',
                                  FieldWildcardQuery(None, 'c*t'))
        self._assert_str_and_repr('animal:d\\??',
                                  'FieldWildcardQuery("animal", "d\\??")',
                                  FieldWildcardQuery('animal', 'd\\??'))

        with self.assertRaises(AssertionError):
            FieldWildcardQuery('large', True)
        with self.assertRaises(AssertionError):
            FieldWildcardQuery('size', 34634)

        self.assertEqual(False, FieldWildcardQuery.is_wildcard_text(''))
        self.assertEqual(False, FieldWildcardQuery.is_wildcard_text('abcde'))
        self.assertEqual(False, FieldWildcardQuery.is_wildcard_text('ab\\? de'))
        self.assertEqual(False, FieldWildcardQuery.is_wildcard_text('ab? de'))
        self.assertEqual(True, FieldWildcardQuery.is_wildcard_text('ab?\\ de'))
        self.assertEqual(True, FieldWildcardQuery.is_wildcard_text('ab?_de'))
        self.assertEqual(True, FieldWildcardQuery.is_wildcard_text('ab*cde'))
        self.assertEqual(True, FieldWildcardQuery.is_wildcard_text('*'))
        self.assertEqual(True, FieldWildcardQuery.is_wildcard_text('?'))
        self.assertEqual(True, FieldWildcardQuery.is_wildcard_text('???'))

        self.assertEqual(1000, FieldValueQuery(None, 'cat').op_precedence())

    def test_field_range(self):
        self._assert_str_and_repr('[0.2 TO 1.6]',
                                  'FieldRangeQuery(None, 0.2, 1.6)',
                                  FieldRangeQuery(None, 0.2, 1.6))
        self._assert_str_and_repr('size:[0.2 TO 1.6]',
                                  'FieldRangeQuery("size", 0.2, 1.6)',
                                  FieldRangeQuery('size', 0.2, 1.6))
        self._assert_str_and_repr('size:{0 TO 100}',
                                  'FieldRangeQuery("size", 0, 100, is_exclusive=True)',
                                  FieldRangeQuery('size', 0, 100, is_exclusive=True))

        self.assertEqual(1000, FieldRangeQuery(None, 0.2, 1.6).op_precedence())

    def test_unary_op(self):
        self._assert_str_and_repr('NOT cat',
                                  'UnaryOpQuery("NOT", FieldValueQuery(None, "cat"))',
                                  UnaryOpQuery('NOT', FieldValueQuery(None, 'cat')))
        self._assert_str_and_repr('+cat',
                                  'UnaryOpQuery("+", FieldValueQuery(None, "cat"))',
                                  UnaryOpQuery('+', FieldValueQuery(None, 'cat')))

        self.assertEqual(800, UnaryOpQuery('NOT', FieldValueQuery(None, 'cat')).op_precedence())

    def test_binary_op(self):
        self._assert_str_and_repr('cat AND dog',
                                  'BinaryOpQuery("AND", FieldValueQuery(None, "cat"), FieldValueQuery(None, "dog"))',
                                  BinaryOpQuery('AND', FieldValueQuery(None, 'cat'),
                                                FieldValueQuery(None, 'dog')))

        self._assert_str_and_repr('NOT snake AND (cat OR dog)',
                                  'BinaryOpQuery("AND", UnaryOpQuery("NOT", FieldValueQuery(None, "snake")),'
                                  ' BinaryOpQuery("OR", FieldValueQuery(None, "cat"), FieldValueQuery(None, "dog")))',
                                  BinaryOpQuery('AND',
                                                UnaryOpQuery('NOT', FieldValueQuery(None, 'snake')),
                                                BinaryOpQuery('OR', FieldValueQuery(None, 'cat'),
                                                              FieldValueQuery(None, 'dog'))))
        self._assert_str_and_repr('(cat OR dog) AND NOT snake',
                                  'BinaryOpQuery("AND", BinaryOpQuery("OR", FieldValueQuery(None, "cat"),'
                                  ' FieldValueQuery(None, "dog")), UnaryOpQuery("NOT", FieldValueQuery(None, "snake")))',
                                  BinaryOpQuery('AND',
                                                BinaryOpQuery('OR', FieldValueQuery(None, 'cat'),
                                                              FieldValueQuery(None, 'dog')),
                                                UnaryOpQuery('NOT', FieldValueQuery(None, 'snake'))))

        self.assertEqual(600, BinaryOpQuery('AND',
                                            FieldValueQuery(None, 'cat'),
                                            FieldValueQuery(None, 'dog')).op_precedence())
        self.assertEqual(500, BinaryOpQuery('OR',
                                            FieldValueQuery(None, 'cat'),
                                            FieldValueQuery(None, 'dog')).op_precedence())

    def test_phrase(self):
        self._assert_str_and_repr('animal:cat dog',
                                  'PhraseQuery([FieldValueQuery("animal", "cat"), FieldValueQuery(None, "dog")])',
                                  PhraseQuery([FieldValueQuery('animal', 'cat'),
                                               FieldValueQuery(None, "dog")]))

        self.assertEqual(400, PhraseQuery([FieldValueQuery(None, 'cat'),
                                           FieldValueQuery(None, 'dog')]).op_precedence())

    def test_accept(self):
        qt = PhraseQuery([FieldValueQuery(None, 'mouse'),
                          UnaryOpQuery("-", FieldValueQuery(None, 'snake')),
                          FieldValueQuery(name='size', value=15),
                          FieldRangeQuery(name='size', start_value=4, end_value=12),
                          BinaryOpQuery("AND", FieldValueQuery(None, "dog"), FieldValueQuery(None, 'cat'))])
        self.assertEqual('mouse | -(snake) | size:15 | size:[4 TO 12] | AND(dog, cat)',
                         qt.accept(CollectingQueryVisitor()))


class CollectingQueryVisitor(QueryVisitor[str]):

    def visit_phrase(self, qt: PhraseQuery, terms: List[str]) -> Optional[str]:
        return ' | '.join(terms)

    def visit_unary_op(self, qt: UnaryOpQuery, term: str) -> Optional[str]:
        return f'{qt.op}({term})'

    def visit_binary_op(self, qt: BinaryOpQuery, term1: str, term2: str) -> Optional[str]:
        return f'{qt.op}({term1}, {term2})'

    def visit_field_value(self, qt: FieldValueQuery) -> Optional[str]:
        return str(qt)

    def visit_field_wildcard(self, qt: FieldWildcardQuery) -> Optional[str]:
        return str(qt)

    def visit_field_range(self, qt: FieldRangeQuery) -> Optional[str]:
        return str(qt)
