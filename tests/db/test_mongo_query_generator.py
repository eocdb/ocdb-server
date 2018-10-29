import unittest

from eocdb.core import QueryParser
from eocdb.db.mongo_query_generator import MongoQueryGenerator


class TestMongoQueryGenerator(unittest.TestCase):

    def setUp(self):
        self.mongo_gen = MongoQueryGenerator()

    def test_empty_query(self):
        self.assertEqual(None, self.mongo_gen.query)

    def test_query_field_value_equal_string(self):
        q = QueryParser.parse('investigators:Robert_Vaillancourt')
        q.accept(self.mongo_gen)

        self.assertEqual({'metadata.investigators' : 'Robert_Vaillancourt'}, self.mongo_gen.query)

    def test_query_field_value_equal_float(self):
        q = QueryParser.parse('north_latitude:42.4853')
        q.accept(self.mongo_gen)

        self.assertEqual({'metadata.north_latitude' : 42.4853}, self.mongo_gen.query)

    def test_query_field_values_AND(self):
        q = QueryParser.parse('cruise:KN219 AND data_type:bottle')
        q.accept(self.mongo_gen)

        self.assertEqual({'metadata.cruise' : 'KN219', 'metadata.data_type' : 'bottle'}, self.mongo_gen.query)

    def test_query_field_values_OR(self):
        q = QueryParser.parse('cruise:KN219 OR data_type:bottle')
        q.accept(self.mongo_gen)

        self.assertEqual({'$or': [{'metadata.cruise' : 'KN219'}, {'metadata.data_type' : 'bottle'}]}, self.mongo_gen.query)

    def test_query_field_value_range(self):
        q = QueryParser.parse('south_latitude:[-25.6 TO -22.5]')
        q.accept(self.mongo_gen)

        self.assertEqual({'metadata.south_latitude' : {'$gte' : -25.6, '$lte' : -22.5}}, self.mongo_gen.query)

    def test_query_field_value_single_char_wildcard(self):
        q = QueryParser.parse('investigators:Steven_?_Effler')
        q.accept(self.mongo_gen)

        self.assertEqual({'metadata.investigators' : {'$regex' : 'Steven_._Effler'}}, self.mongo_gen.query)

    def test_query_field_value_multiple_single_char_wildcard(self):
        q = QueryParser.parse('investigators:St?ven_?_Ef?ler')
        q.accept(self.mongo_gen)

        self.assertEqual({'metadata.investigators' : {'$regex' : 'St.ven_._Ef.ler'}}, self.mongo_gen.query)

    def test_query_field_value_multiple_char_wildcard(self):
        q = QueryParser.parse('investigators:Steven*Effler')
        q.accept(self.mongo_gen)

        self.assertEqual({'metadata.investigators' : {'$regex' : 'Steven.*Effler'}}, self.mongo_gen.query)

    def test_query_field_value_multiple_multiple_char_wildcard(self):
        q = QueryParser.parse('investigators:S*n*Effler')
        q.accept(self.mongo_gen)

        self.assertEqual({'metadata.investigators' : {'$regex' : 'S.*n.*Effler'}}, self.mongo_gen.query)

    def test_get_db_field_name(self):
        self.assertEqual("metadata.wamp", self.mongo_gen._get_db_field_name("wamp"))

        self.assertEqual("path", self.mongo_gen._get_db_field_name("path"))
        self.assertEqual("status", self.mongo_gen._get_db_field_name("status"))
