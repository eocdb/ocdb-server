import datetime
import unittest

from eocdb.core.models import DatasetQuery
from eocdb.db.mongo_db_driver import MongoDbDriver


class TestMongoQueryConverter(unittest.TestCase):

    def setUp(self):
        self.converter = MongoDbDriver.QueryConverter()

    def test_to_dict_empty(self):
        dict = self.converter.to_dict(DatasetQuery())
        self.assertEqual({}, dict)

    def test_to_dict_expression(self):
        dict = self.converter.to_dict(DatasetQuery(expr="bananas:many"))
        self.assertEqual({'metadata.bananas': 'many'}, dict)

    def test_to_dict_region(self):
        query = DatasetQuery(region=[11, -18, 12, -17.4])
        dict = self.converter.to_dict(query)
        self.assertEqual({'latitudes': {'$gte': -18, '$lte': -17.4},
                          'longitudes': {'$gte': 11, '$lte': 12}}, dict)

    def test_to_dict_times_start_to_stop(self):
        query = DatasetQuery(time=["2016-01-01T00:00:00", "2016-01-01T04:00:00"])
        dict = self.converter.to_dict(query)
        self.assertEqual({'times': {'$gte': datetime.datetime(2016, 1, 1, 0, 0),
                                    '$lte': datetime.datetime(2016, 1, 1, 4, 0)}}, dict)

    def test_to_dict_times_no_start(self):
        query = DatasetQuery(time=[None, "2016-01-01T04:00:00"])
        dict = self.converter.to_dict(query)
        self.assertEqual({'times': {'$lte': datetime.datetime(2016, 1, 1, 4, 0)}}, dict)

    def test_to_dict_times_no_stop(self):
        query = DatasetQuery(time=["2016-01-01T00:00:00", None])
        dict = self.converter.to_dict(query)
        self.assertEqual({'times': {'$gte': datetime.datetime(2016, 1, 1, 0, 0)}}, dict)

    def test_to_dict_both_None(self):
        query = DatasetQuery(time=[None, None])
        try:
            self.converter.to_dict(query)
            self.fail("ValueError expected")
        except ValueError:
            pass

    def test_to_dict_one_pgroup(self):
        query = DatasetQuery(pgroup=["sal"])

        dict = self.converter.to_dict(query)
        self.assertEqual({'attributes': {'$in': ['sal']}}, dict)

    def test_to_dict_two_pgroup(self):
        query = DatasetQuery(pgroup=["sal", "Chl"])

        dict = self.converter.to_dict(query)
        self.assertEqual({'attributes': {'$in': ['sal', 'Chl']}}, dict)

    def test_to_dict_mtype_all(self):
        query = DatasetQuery(mtype='all')

        dict = self.converter.to_dict(query)
        self.assertEqual({}, dict)

    def test_to_dict_mtype_brdf(self):
        query = DatasetQuery(mtype='brdf')

        dict = self.converter.to_dict(query)
        self.assertEqual({'metadata.data_type': 'brdf'}, dict)

