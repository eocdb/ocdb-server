import datetime
import unittest

from eocdb.core.models import DatasetQuery
from eocdb.db.mongo_db_driver import MongoDbDriver


class TestMongoQueryConverter(unittest.TestCase):

    def test_to_dict_empty(self):
        converter = MongoDbDriver.QueryConverter()

        dict = converter.to_dict(DatasetQuery())
        self.assertEqual({}, dict)

    def test_to_dict_expression(self):
        converter = MongoDbDriver.QueryConverter()

        dict = converter.to_dict(DatasetQuery(expr="bananas:many"))
        self.assertEqual({'metadata.bananas': 'many'}, dict)

    def test_to_dict_region(self):
        converter = MongoDbDriver.QueryConverter()

        query = DatasetQuery(region=[11, -18, 12, -17.4])
        dict = converter.to_dict(query)
        self.assertEqual({'latitudes': {'$gte': -18, '$lte': -17.4},
                          'longitudes': {'$gte': 11, '$lte': 12}}, dict)

    def test_to_dict_times_start_to_stop(self):
        converter = MongoDbDriver.QueryConverter()

        query = DatasetQuery(time=["2016-01-01T00:00:00", "2016-01-01T04:00:00"])
        dict = converter.to_dict(query)
        self.assertEqual({'times': {'$gte': datetime.datetime(2016, 1, 1, 0, 0),
                                    '$lte': datetime.datetime(2016, 1, 1, 4, 0)}}, dict)

    def test_to_dict_times_no_start(self):
        converter = MongoDbDriver.QueryConverter()

        query = DatasetQuery(time=[None, "2016-01-01T04:00:00"])
        dict = converter.to_dict(query)
        self.assertEqual({'times': {'$lte': datetime.datetime(2016, 1, 1, 4, 0)}}, dict)

    def test_to_dict_times_no_stop(self):
        converter = MongoDbDriver.QueryConverter()

        query = DatasetQuery(time=["2016-01-01T00:00:00", None])
        dict = converter.to_dict(query)
        self.assertEqual({'times': {'$gte': datetime.datetime(2016, 1, 1, 0, 0)}}, dict)

    def test_to_dict_both_None(self):
        converter = MongoDbDriver.QueryConverter()

        query = DatasetQuery(time=[None, None])
        try:
            converter.to_dict(query)
            self.fail("ValueError expected")
        except ValueError:
            pass
