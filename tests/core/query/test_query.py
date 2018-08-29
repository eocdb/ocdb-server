from typing import Optional, List
from unittest import TestCase

from eocdb.core.query.query import TextQuery, PhraseQuery, UnaryOpQuery, BinaryOpQuery, QueryVisitor, RangeQuery


class QueryTest(TestCase):
    def _assert_str_and_repr(self, expected_str, expected_repr, term):
        self.assertEqual(expected_str, str(term))
        self.assertEqual(expected_repr, repr(term))

    def test_text(self):
        self._assert_str_and_repr('cat',
                                  'TextQuery("cat")',
                                  TextQuery('cat'))
        self._assert_str_and_repr('animal:cat',
                                  'TextQuery("cat", name="animal")',
                                  TextQuery('cat', name='animal'))
        self._assert_str_and_repr('c*t',
                                  'TextQuery("c*t")',
                                  TextQuery('c*t'))
        self._assert_str_and_repr('animal:"cat dog"',
                                  'TextQuery("cat dog", name="animal", is_quoted=True)',
                                  TextQuery('cat dog', is_quoted=True, name='animal'))

        self.assertEqual(1000, TextQuery('cat').op_precedence())

    def test_range(self):
        self._assert_str_and_repr('[0.2 TO 1.6]',
                                  'RangeQuery(0.2, 1.6)',
                                  RangeQuery(0.2, 1.6))
        self._assert_str_and_repr('size:[0.2 TO 1.6]',
                                  'RangeQuery(0.2, 1.6, name="size")',
                                  RangeQuery(0.2, 1.6, name='size'))
        self._assert_str_and_repr('size:{0 TO 100}',
                                  'RangeQuery(0, 100, name="size", is_exclusive=True)',
                                  RangeQuery(0, 100, name='size', is_exclusive=True))

        self.assertEqual(1000, RangeQuery(0.2, 1.6).op_precedence())

    def test_unary_op(self):
        self._assert_str_and_repr('NOT cat',
                                  'UnaryOpQuery("NOT", TextQuery("cat"))',
                                  UnaryOpQuery('NOT', TextQuery('cat')))
        self._assert_str_and_repr('+cat',
                                  'UnaryOpQuery("+", TextQuery("cat"))',
                                  UnaryOpQuery('+', TextQuery('cat')))

        self.assertEqual(800, UnaryOpQuery('NOT', TextQuery('cat')).op_precedence())

    def test_binary_op(self):
        self._assert_str_and_repr('cat AND dog',
                                  'BinaryOpQuery("AND", TextQuery("cat"), TextQuery("dog"))',
                                  BinaryOpQuery('AND', TextQuery('cat'), TextQuery('dog')))

        self._assert_str_and_repr('NOT snake AND (cat OR dog)',
                                  'BinaryOpQuery("AND", UnaryOpQuery("NOT", TextQuery("snake")),'
                                  ' BinaryOpQuery("OR", TextQuery("cat"), TextQuery("dog")))',
                                  BinaryOpQuery('AND',
                                                UnaryOpQuery('NOT', TextQuery('snake')),
                                                BinaryOpQuery('OR', TextQuery('cat'), TextQuery('dog'))))
        self._assert_str_and_repr('(cat OR dog) AND NOT snake',
                                  'BinaryOpQuery("AND", BinaryOpQuery("OR", TextQuery("cat"),'
                                  ' TextQuery("dog")), UnaryOpQuery("NOT", TextQuery("snake")))',
                                  BinaryOpQuery('AND',
                                                BinaryOpQuery('OR', TextQuery('cat'), TextQuery('dog')),
                                                UnaryOpQuery('NOT', TextQuery('snake'))))

        self.assertEqual(600, BinaryOpQuery('AND', TextQuery('cat'), TextQuery('dog')).op_precedence())
        self.assertEqual(500, BinaryOpQuery('OR', TextQuery('cat'), TextQuery('dog')).op_precedence())

    def test_phrase(self):
        self._assert_str_and_repr('animal:cat dog',
                                  'PhraseQuery([TextQuery("cat", name="animal"), TextQuery("dog")])',
                                  PhraseQuery([TextQuery('cat', name='animal'), TextQuery("dog")]))

        self.assertEqual(400, PhraseQuery([TextQuery('cat'), TextQuery('dog')]).op_precedence())

    def test_accept(self):
        qt = PhraseQuery([TextQuery('mouse'),
                          UnaryOpQuery("-", TextQuery('snake')),
                          RangeQuery(4, 12, name='size'),
                          BinaryOpQuery("AND", TextQuery("dog"), TextQuery('cat'))])
        self.assertEqual('mouse | -(snake) | size:[4 TO 12] | AND(dog, cat)',
                         qt.accept(CollectingQueryVisitor()))


class CollectingQueryVisitor(QueryVisitor[str]):

    def visit_phrase(self, qt: PhraseQuery, terms: List[str]) -> Optional[str]:
        return ' | '.join(terms)

    def visit_unary_op(self, qt: UnaryOpQuery, term: str) -> Optional[str]:
        return f'{qt.op}({term})'

    def visit_binary_op(self, qt: BinaryOpQuery, term1: str, term2: str) -> Optional[str]:
        return f'{qt.op}({term1}, {term2})'

    def visit_text(self, qt: TextQuery) -> Optional[str]:
        return str(qt)

    def visit_range(self, qt: RangeQuery) -> Optional[str]:
        return str(qt)
