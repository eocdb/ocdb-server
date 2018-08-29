from typing import Optional, List
from unittest import TestCase

from eocdb.core.query.query import TextQuery, PhraseQuery, UnaryOpQuery, BinaryOpQuery, QueryVisitor


class QueryTest(TestCase):
    def _assert_str_and_repr(self, expected_str, expected_repr, term):
        self.assertEqual(expected_str, str(term))
        self.assertEqual(expected_repr, repr(term))

    def test_str_and_repr(self):
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

        self._assert_str_and_repr('+cat',
                                  'UnaryOpQuery("+", TextQuery("cat"))',
                                  UnaryOpQuery('+', TextQuery('cat')))

        self._assert_str_and_repr('cat AND dog',
                                  'BinaryOpQuery("AND", TextQuery("cat"), TextQuery("dog"))',
                                  BinaryOpQuery('AND', TextQuery('cat'), TextQuery('dog')))

        self._assert_str_and_repr('animal:cat dog',
                                  'PhraseQuery([TextQuery("cat", name="animal"), TextQuery("dog")])',
                                  PhraseQuery([TextQuery('cat', name='animal'), TextQuery("dog")]))

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

    def test_accept(self):
        qt = PhraseQuery([TextQuery('mouse'),
                          UnaryOpQuery("-", TextQuery('snake')),
                          BinaryOpQuery("AND", TextQuery("dog"), TextQuery('cat'))])
        self.assertEqual('mouse | -(snake) | AND(dog, cat)',
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
