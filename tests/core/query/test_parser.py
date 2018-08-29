from unittest import TestCase

from eocdb.core.query.parser import QueryTokenizer, QuerySyntaxError, QueryParser, TextQuery, PhraseQuery, UnaryOpQuery, \
    BinaryOpQuery


class QueryParserTest(TestCase):
    def test_simple(self):
        self.assertEqual(None,
                         QueryParser.parse(""))
        self.assertEqual(None,
                         QueryParser.parse("   "))
        self.assertEqual(TextQuery("cat"),
                         QueryParser.parse("cat"))
        self.assertEqual(PhraseQuery([TextQuery("cat"), TextQuery("dog")]),
                         QueryParser.parse("cat dog"))
        self.assertEqual(BinaryOpQuery('AND', TextQuery("cat"), TextQuery("dog")),
                         QueryParser.parse("cat AND  dog "))
        self.assertEqual(TextQuery("cat", name='type'),
                         QueryParser.parse("type:cat"))
        self.assertEqual(PhraseQuery([UnaryOpQuery('+', TextQuery("cat")), UnaryOpQuery('-', TextQuery("dog"))]),
                         QueryParser.parse("+cat -dog"))


class QueryTokenizerTest(TestCase):
    def test_text(self):
        self.assertEqual([],
                         QueryTokenizer.tokenize(""))
        self.assertEqual([],
                         QueryTokenizer.tokenize("   "))
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
