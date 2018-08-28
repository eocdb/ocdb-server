from typing import Optional, Any, List
from unittest import TestCase

from eocdb.core.queryparser import QueryTokenizer, QuerySyntaxError, QueryParser, QTText, QTList, QTUnOp, QTBinOp, \
    QTVisitor


class QueryParserTest(TestCase):
    def test_simple(self):
        self.assertEqual(None,
                         QueryParser.parse(""))
        self.assertEqual(None,
                         QueryParser.parse("   "))
        self.assertEqual(QTText("cat"),
                         QueryParser.parse("cat"))
        self.assertEqual(QTList([QTText("cat"), QTText("dog")]),
                         QueryParser.parse("cat dog"))
        self.assertEqual(QTBinOp('AND', QTText("cat"), QTText("dog")),
                         QueryParser.parse("cat AND  dog "))
        self.assertEqual(QTText("cat", name='type'),
                         QueryParser.parse("type:cat"))
        self.assertEqual(QTList([QTUnOp('+', QTText("cat")), QTUnOp('-', QTText("dog"))]),
                         QueryParser.parse("+cat -dog"))


class QTTest(TestCase):
    def _assert_str_and_repr(self, expected_str, expected_repr, term):
        self.assertEqual(expected_str, str(term))
        self.assertEqual(expected_repr, repr(term))

    def test_str_and_repr(self):
        self._assert_str_and_repr('cat',
                                  'QTText("cat")',
                                  QTText('cat'))
        self._assert_str_and_repr('animal:cat',
                                  'QTText("cat", name="animal")',
                                  QTText('cat', name='animal'))
        self._assert_str_and_repr('c*t',
                                  'QTText("c*t", is_wildcard=True)',
                                  QTText('c*t', is_wildcard=True))
        self._assert_str_and_repr('"cat"',
                                  'QTText("cat", is_exact=True)',
                                  QTText('cat', is_exact=True, name=None))
        self._assert_str_and_repr('animal:"cat"',
                                  'QTText("cat", name="animal", is_exact=True)',
                                  QTText('cat', is_exact=True, name='animal'))

        self._assert_str_and_repr('+cat',
                                  'QTUnOp("+", QTText("cat"))',
                                  QTUnOp('+', QTText('cat')))

        self._assert_str_and_repr('cat AND dog',
                                  'QTBinOp("AND", QTText("cat"), QTText("dog"))',
                                  QTBinOp('AND', QTText('cat'), QTText('dog')))

        self._assert_str_and_repr('animal:cat dog',
                                  'QTList([QTText("cat", name="animal"), QTText("dog")])',
                                  QTList([QTText('cat', name='animal'), QTText("dog")]))

        self._assert_str_and_repr('NOT snake AND (cat OR dog)',
                                  'QTBinOp("AND", QTUnOp("NOT", QTText("snake")),'
                                  ' QTBinOp("OR", QTText("cat"), QTText("dog")))',
                                  QTBinOp('AND',
                                          QTUnOp('NOT', QTText('snake')),
                                          QTBinOp('OR', QTText('cat'), QTText('dog'))))
        self._assert_str_and_repr('(cat OR dog) AND NOT snake',
                                  'QTBinOp("AND", QTBinOp("OR", QTText("cat"),'
                                  ' QTText("dog")), QTUnOp("NOT", QTText("snake")))',
                                  QTBinOp('AND',
                                          QTBinOp('OR', QTText('cat'), QTText('dog')),
                                          QTUnOp('NOT', QTText('snake'))))

    def test_accept(self):
        qt = QTList([QTText('mouse'),
                     QTUnOp("-", QTText('snake')),
                     QTBinOp("AND", QTText("dog"), QTText('cat'))])
        self.assertEqual('mouse | -(snake) | AND(dog, cat)',
                         qt.accept(CollectingQTVisitor()))


class QueryTokenizerTest(TestCase):
    def test_text(self):
        self.assertEqual([],
                         QueryTokenizer.tokenize(""))
        self.assertEqual([],
                         QueryTokenizer.tokenize("   "))
        self.assertEqual([('TEXT', 'cat')],
                         QueryTokenizer.tokenize("cat"))
        self.assertEqual([('TEXT', 'cat'),
                          ('TEXT', 'dog')],
                         QueryTokenizer.tokenize("cat dog"))
        self.assertEqual([('TEXT', 'cat'),
                          ('KEYWORD', 'AND'),
                          ('TEXT', 'dog')],
                         QueryTokenizer.tokenize("cat AND  dog "))
        self.assertEqual([('TEXT', 'type'),
                          ('CONTROL', ':'),
                          ('TEXT', 'cat')],
                         QueryTokenizer.tokenize("type:cat"))
        self.assertEqual([('TEXT', 'type:cat')],
                         QueryTokenizer.tokenize("type\\:cat"))

    def test_unary(self):
        self.assertEqual([('CONTROL', '+'),
                          ('TEXT', 'cat'),
                          ('CONTROL', '-'),
                          ('TEXT', 'dog')],
                         QueryTokenizer.tokenize("+cat -dog"))

    def test_quoted_text(self):
        self.assertEqual([('QUOTED_TEXT', 'type: cat')],
                         QueryTokenizer.tokenize("'type: cat'"))
        self.assertEqual([('QUOTED_TEXT', 'cat AND  dog ')],
                         QueryTokenizer.tokenize('"cat AND  dog "'))

        with self.assertRaises(QuerySyntaxError) as cm:
            QueryTokenizer.tokenize('"cat AND  dog')
        self.assertEqual('Missing matching ["]', f'{cm.exception}')

    def test_nested(self):
        self.assertEqual([('CONTROL', '('),
                          ('TEXT', 'cat'),
                          ('KEYWORD', 'OR'),
                          ('TEXT', 'dog'),
                          ('CONTROL', ')'),
                          ('KEYWORD', 'AND'),
                          ('KEYWORD', 'NOT'),
                          ('TEXT', 'snake')],
                         QueryTokenizer.tokenize("(cat OR dog) AND NOT snake"))
        self.assertEqual([('TEXT', 'cat'),
                          ('KEYWORD', 'AND'),
                          ('CONTROL', '('),
                          ('TEXT', 'dog'),
                          ('KEYWORD', 'OR'),
                          ('KEYWORD', 'NOT'),
                          ('TEXT', 'snake'),
                          ('CONTROL', ')')],
                         QueryTokenizer.tokenize("cat AND (dog OR NOT snake)"))

        with self.assertRaises(QuerySyntaxError) as cm:
            QueryTokenizer.tokenize('cat AND (dog OR NOT snake')
        self.assertEqual('Missing matching [)]', f'{cm.exception}')

        with self.assertRaises(QuerySyntaxError) as cm:
            QueryTokenizer.tokenize('cat OR dog) AND NOT snake')
        self.assertEqual('Missing matching [(]', f'{cm.exception}')


class CollectingQTVisitor(QTVisitor[str]):

    def visit_list(self, qt: QTList, terms: List[str]) -> Optional[str]:
        return ' | '.join(terms)

    def visit_unary_op(self, qt: QTUnOp, term: str) -> Optional[str]:
        return f'{qt.op}({term})'

    def visit_binary_op(self, qt: QTBinOp, term1: str, term2: str) -> Optional[str]:
        return f'{qt.op}({term1}, {term2})'

    def visit_text(self, qt: QTText) -> Optional[str]:
        return str(qt)
