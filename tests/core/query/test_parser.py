from unittest import TestCase

from eocdb.core.query.parser import QueryTokenizer, QuerySyntaxError, QueryParser
from eocdb.core.query.query import QueryBuilder

B = QueryBuilder
P = QueryParser
T = QueryTokenizer


class QueryParserTest(TestCase):

    def test_empty(self):
        self.assertEqual(None, P.parse(""))
        self.assertEqual(None, P.parse("   "))

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            P.parse(None)

    def test_field_value(self):
        self.assertEqual(B.value("cat"), P.parse("cat"))
        self.assertEqual(B.value("cat", name='type'), P.parse("type:cat"))
        self.assertEqual(B.value(200), P.parse("200"))
        self.assertEqual(B.value("200"), P.parse('"200"'))
        self.assertEqual(B.value(100, name='size'), P.parse("size:100"))
        self.assertEqual(B.value("100", name='length'), P.parse("length:'100'"))

    def test_field_range(self):
        self.assertEqual(B.inrange(0, 100), P.parse("[0 TO 100]"))
        self.assertEqual(B.inrange(0.5, 100.0), P.parse("[0.5 TO 100]"))
        self.assertEqual(B.inrange("snail", "snake"), P.parse("[snail TO snake]"))
        self.assertEqual(B.inrange("0", "100"), P.parse("['0' TO '100']"))
        self.assertEqual(B.inrange("cat", "100"), P.parse("[cat TO 100]"))
        self.assertEqual(B.inrange(0, 100, name='size'), P.parse("size:[0 TO 100]"))

        self.assertEqual(B.within(0, 100), P.parse("{0 TO 100}"))
        self.assertEqual(B.within(0.5, 100.0), P.parse("{0.5 TO 100}"))
        self.assertEqual(B.within("snail", "snake"), P.parse("{snail TO snake}"))
        self.assertEqual(B.within("0", "100"), P.parse("{'0' TO '100'}"))
        self.assertEqual(B.within("cat", "100"), P.parse("{cat TO 100}"))
        self.assertEqual(B.within(0, 100, name='size'), P.parse("size:{0 TO 100}"))

    def test_field_wildcard(self):
        self.assertEqual(B.wildcard("ca*"), P.parse("ca*"))
        self.assertEqual(B.wildcard("?at"), P.parse("?at"))
        self.assertEqual(B.wildcard("?a*"), P.parse("?a*"))

    def test_unary_op(self):
        self.assertEqual(B.include(B.value("cat")),
                         P.parse("+cat"))
        self.assertEqual(B.exclude(B.value("dog")),
                         P.parse("-dog"))
        self.assertEqual(B.NOT(B.value("bird")),
                         P.parse("NOT bird"))
        self.assertEqual(B.NOT(B.NOT(B.value("bird"))),
                         P.parse("NOT NOT bird"))

    def test_binary_op(self):
        self.assertEqual(B.OR(B.value("cat"), B.value("dog")),
                         P.parse(" cat OR dog"))
        self.assertEqual(B.AND(B.value("cat"), B.value("dog")),
                         P.parse("cat AND  dog "))
        self.assertEqual(B.AND(B.value("cat"), B.AND(B.value("dog"), B.value("bird"))),
                         P.parse("cat AND dog AND bird"))
        self.assertEqual(B.OR(B.AND(B.value("cat"), B.value("dog")), B.value("bird")),
                         P.parse("cat AND dog OR bird"))
        self.assertEqual(B.OR(B.value("cat"), B.AND(B.value("dog"), B.value("bird"))),
                         P.parse("cat OR dog AND bird"))

        self.assertEqual(B.AND(B.inrange(107, 110, name="lon"), B.inrange(-40, -35, name="lat")),
                         P.parse("lon:[107 TO 110] AND lat:[-40 TO -35]"))

    def test_group(self):
        self.assertEqual(B.AND(B.OR(B.value("cat"),
                                    B.value("dog")),
                               B.value("bird")),
                         P.parse("(cat OR dog) AND bird"))
        self.assertEqual(B.AND(B.value("cat"),
                               B.OR(B.value("dog"),
                                    B.value("bird"))),
                         P.parse("cat AND (dog OR bird)"))

        self.assertEqual(B.AND(B.value("cat", name="animal"),
                               B.OR(B.value("dog", name="animal"),
                                    B.value("bird", name="animal"))),
                         P.parse("animal:(cat AND (dog OR bird))"))

    def test_phrase(self):
        self.assertEqual(B.phrase(B.value("cat"), B.value("dog")),
                         P.parse("cat dog"))
        self.assertEqual(B.phrase(B.include(B.value("cat")), B.exclude(B.value("dog")), B.value("mouse", name='b')),
                         P.parse("+cat -dog b:mouse"))


class QueryTokenizerTest(TestCase):
    def test_empty(self):
        self.assertEqual([],
                         T.tokenize(""))
        self.assertEqual([],
                         T.tokenize("   "))

    def test_values(self):
        self.assertEqual([('TEXT', 'cat', 0)],
                         T.tokenize("cat"))
        self.assertEqual([('TEXT', 'cat', 0),
                          ('TEXT', 'dog', 4)],
                         T.tokenize("cat dog"))
        self.assertEqual([('TEXT', 'cat', 0),
                          ('KEYWORD', 'AND', 4),
                          ('TEXT', 'dog', 9)],
                         T.tokenize("cat AND  dog "))
        self.assertEqual([('TEXT', 'type', 0),
                          ('CONTROL', ':', 4),
                          ('TEXT', 'cat', 5)],
                         T.tokenize("type:cat"))
        self.assertEqual([('TEXT', 'type\\:cat', 0)],
                         T.tokenize("type\\:cat"))
        self.assertEqual([('NUMBER', 29385, 0)],
                         T.tokenize("29385"))
        self.assertEqual([('NUMBER', -29.385, 0)],
                         T.tokenize("-29.385"))
        self.assertEqual([('TEXT', 'cat', 0),
                          ('NUMBER', 255678, 4)],
                         T.tokenize("cat 255678"))

    def test_unary(self):
        self.assertEqual([('CONTROL', '+', 0),
                          ('TEXT', 'cat', 1),
                          ('CONTROL', '-', 5),
                          ('TEXT', 'dog', 6)],
                         T.tokenize("+cat -dog"))

    def test_quoted_text(self):
        self.assertEqual([('QTEXT', 'type: cat', 1)],
                         T.tokenize("'type: cat'"))
        self.assertEqual([('QTEXT', 'cat AND  dog ', 1)],
                         T.tokenize('"cat AND  dog "'))

        with self.assertRaises(QuerySyntaxError) as cm:
            T.tokenize('"cat AND  dog')
        self.assertEqual('Missing matching ["]', f'{cm.exception}')

    def test_range(self):
        self.assertEqual([('CONTROL', '[', 0),
                          ('NUMBER', 0.1, 1),
                          ('TEXT', 'TO', 5),
                          ('NUMBER', 0.9, 8),
                          ('CONTROL', ']', 11)],
                         T.tokenize('[0.1 TO 0.9]'))

    def test_nested(self):
        self.assertEqual([('CONTROL', '(', 0),
                          ('TEXT', 'cat', 1),
                          ('KEYWORD', 'OR', 5),
                          ('TEXT', 'dog', 8),
                          ('CONTROL', ')', 11),
                          ('KEYWORD', 'AND', 13),
                          ('KEYWORD', 'NOT', 17),
                          ('TEXT', 'snake', 21)],
                         T.tokenize("(cat OR dog) AND NOT snake"))
        self.assertEqual([('TEXT', 'cat', 0),
                          ('KEYWORD', 'AND', 4),
                          ('CONTROL', '(', 8),
                          ('TEXT', 'dog', 9),
                          ('KEYWORD', 'OR', 13),
                          ('KEYWORD', 'NOT', 16),
                          ('TEXT', 'snake', 20),
                          ('CONTROL', ')', 25)],
                         T.tokenize("cat AND (dog OR NOT snake)"))

        with self.assertRaises(QuerySyntaxError) as cm:
            T.tokenize('cat AND (dog OR NOT snake')
        self.assertEqual('Missing matching [)]', f'{cm.exception}')

        with self.assertRaises(QuerySyntaxError) as cm:
            T.tokenize('cat OR dog) AND NOT snake')
        self.assertEqual('Missing matching [(]', f'{cm.exception}')

    def test_field_range(self):
        self.assertEqual([('QTEXT', 'type: cat', 1)],
                         T.tokenize("'type: cat'"))
        self.assertEqual([('QTEXT', 'cat AND  dog ', 1)],
                         T.tokenize('"cat AND  dog "'))

        with self.assertRaises(QuerySyntaxError) as cm:
            T.tokenize('"cat AND  dog')
        self.assertEqual('Missing matching ["]', f'{cm.exception}')

    def test_group(self):
        self.assertEqual([('TEXT', 'animal', 0),
                          ('CONTROL', ':', 6),
                          ('CONTROL', '(', 7),
                          ('TEXT', 'cat', 8),
                          ('KEYWORD', 'AND', 12),
                          ('CONTROL', '(', 16),
                          ('TEXT', 'dog', 17),
                          ('KEYWORD', 'OR', 21),
                          ('TEXT', 'bird', 24),
                          ('CONTROL', ')', 28),
                          ('CONTROL', ')', 29)],
                         T.tokenize("animal:(cat AND (dog OR bird))"))
