from unittest import TestCase

from eocdb.core.query.parser import QueryTokenizer, QuerySyntaxError, QueryParser
from eocdb.core.query.query import QueryBuilder

b = QueryBuilder
p = QueryParser


class QueryParserTest(TestCase):
    def test_empty(self):
        self.assertEqual(None, p.parse(""))
        self.assertEqual(None, p.parse("   "))

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            p.parse(None)

    def test_field_value(self):
        self.assertEqual(b.value("cat"), p.parse("cat"))
        self.assertEqual(b.value("cat", name='type'), p.parse("type:cat"))
        self.assertEqual(b.value(200), p.parse("200"))
        #self.assertEqual(b.value(100, name='size'), p.parse("size:100"))
        #self.assertEqual(b.value("100", name='length'), p.parse("length:'100'"))

    def test_field_wildcard(self):
        self.assertEqual(b.wildcard("ca*"), p.parse("ca*"))
        self.assertEqual(b.wildcard("?at"), p.parse("?at"))
        self.assertEqual(b.wildcard("?a*"), p.parse("?a*"))

    def test_unary_op(self):
        self.assertEqual(b.include(b.value("cat")),
                         p.parse("+cat"))
        self.assertEqual(b.exclude(b.value("dog")),
                         p.parse("-dog"))
        self.assertEqual(b.NOT(b.value("bird")),
                         p.parse("NOT bird"))
        self.assertEqual(b.NOT(b.NOT(b.value("bird"))),
                         p.parse("NOT NOT bird"))

    def test_binary_op(self):
        self.assertEqual(b.OR(b.value("cat"), b.value("dog")),
                         p.parse(" cat OR dog"))
        self.assertEqual(b.AND(b.value("cat"), b.value("dog")),
                         p.parse("cat AND  dog "))
        self.assertEqual(b.AND(b.value("cat"), b.AND(b.value("dog"), b.value("bird"))),
                         p.parse("cat AND dog AND bird"))
        self.assertEqual(b.OR(b.AND(b.value("cat"), b.value("dog")), b.value("bird")),
                         p.parse("cat AND dog OR bird"))
        self.assertEqual(b.OR(b.value("cat"), b.AND(b.value("dog"), b.value("bird"))),
                         p.parse("cat OR dog AND bird"))

    def test_group(self):
        self.assertEqual(b.AND(b.OR(b.value("cat"), b.value("dog")), b.value("bird")),
                         p.parse("(cat OR dog) AND bird"))
        self.assertEqual(b.AND(b.value("cat"), b.OR(b.value("dog"), b.value("bird"))),
                         p.parse("cat AND (dog OR bird)"))

    def test_phrase(self):
        self.assertEqual(b.phrase(b.value("cat"), b.value("dog")),
                         p.parse("cat dog"))
        self.assertEqual(b.phrase(b.include(b.value("cat")), b.exclude(b.value("dog")), b.value("mouse", name='b')),
                         p.parse("+cat -dog b:mouse"))


class QueryTokenizerTest(TestCase):
    def test_empty(self):
        self.assertEqual([],
                         QueryTokenizer.tokenize(""))
        self.assertEqual([],
                         QueryTokenizer.tokenize("   "))


    def test_values(self):
        self.assertEqual([('TEXT', 'cat', 0)],
                         QueryTokenizer.tokenize("cat"))
        self.assertEqual([('TEXT', 'cat', 0),
                          ('TEXT', 'dog', 4)],
                         QueryTokenizer.tokenize("cat dog"))
        self.assertEqual([('TEXT', 'cat', 0),
                          ('KEYWORD', 'AND', 4),
                          ('TEXT', 'dog', 9)],
                         QueryTokenizer.tokenize("cat AND  dog "))
        self.assertEqual([('TEXT', 'type', 0),
                          ('CONTROL', ':', 4),
                          ('TEXT', 'cat', 5)],
                         QueryTokenizer.tokenize("type:cat"))
        self.assertEqual([('TEXT', 'type\\:cat', 0)],
                         QueryTokenizer.tokenize("type\\:cat"))
        self.assertEqual([('NUMBER', 29385, 0)],
                         QueryTokenizer.tokenize("29385"))
        self.assertEqual([('TEXT', 'cat', 0),
                          ('NUMBER', 255678, 4)],
                         QueryTokenizer.tokenize("cat 255678"))

    def test_unary(self):
        self.assertEqual([('CONTROL', '+', 0),
                          ('TEXT', 'cat', 1),
                          ('CONTROL', '-', 5),
                          ('TEXT', 'dog', 6)],
                         QueryTokenizer.tokenize("+cat -dog"))

    def test_quoted_text(self):
        self.assertEqual([('QTEXT', 'type: cat', 1)],
                         QueryTokenizer.tokenize("'type: cat'"))
        self.assertEqual([('QTEXT', 'cat AND  dog ', 1)],
                         QueryTokenizer.tokenize('"cat AND  dog "'))

        with self.assertRaises(QuerySyntaxError) as cm:
            QueryTokenizer.tokenize('"cat AND  dog')
        self.assertEqual('Missing matching ["]', f'{cm.exception}')

    def test_nested(self):
        self.assertEqual([('CONTROL', '(', 0),
                          ('TEXT', 'cat', 1),
                          ('KEYWORD', 'OR', 5),
                          ('TEXT', 'dog', 8),
                          ('CONTROL', ')', 11),
                          ('KEYWORD', 'AND', 13),
                          ('KEYWORD', 'NOT', 17),
                          ('TEXT', 'snake', 21)],
                         QueryTokenizer.tokenize("(cat OR dog) AND NOT snake"))
        self.assertEqual([('TEXT', 'cat', 0),
                          ('KEYWORD', 'AND', 4),
                          ('CONTROL', '(', 8),
                          ('TEXT', 'dog', 9),
                          ('KEYWORD', 'OR', 13),
                          ('KEYWORD', 'NOT', 16),
                          ('TEXT', 'snake', 20),
                          ('CONTROL', ')', 25)],
                         QueryTokenizer.tokenize("cat AND (dog OR NOT snake)"))

        with self.assertRaises(QuerySyntaxError) as cm:
            QueryTokenizer.tokenize('cat AND (dog OR NOT snake')
        self.assertEqual('Missing matching [)]', f'{cm.exception}')

        with self.assertRaises(QuerySyntaxError) as cm:
            QueryTokenizer.tokenize('cat OR dog) AND NOT snake')
        self.assertEqual('Missing matching [(]', f'{cm.exception}')

    def test_field_range(self):
        self.assertEqual([('QTEXT', 'type: cat', 1)],
                         QueryTokenizer.tokenize("'type: cat'"))
        self.assertEqual([('QTEXT', 'cat AND  dog ', 1)],
                         QueryTokenizer.tokenize('"cat AND  dog "'))

        with self.assertRaises(QuerySyntaxError) as cm:
            QueryTokenizer.tokenize('"cat AND  dog')
        self.assertEqual('Missing matching ["]', f'{cm.exception}')
