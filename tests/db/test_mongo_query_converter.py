import datetime
import unittest

from eocdb.core.models import DatasetQuery
from eocdb.db.mongo_db_driver import MongoDbDriver


class TestMongoQueryConverter(unittest.TestCase):

    def setUp(self):
        self.converter = MongoDbDriver.QueryConverter()

    def test_to_dict_empty(self):
        mongo_dict = self.converter.to_dict(DatasetQuery())
        self.assertEqual({}, mongo_dict)

    def test_to_dict_expression(self):
        mongo_dict = self.converter.to_dict(DatasetQuery(expr="bananas:many"))
        self.assertEqual({'metadata.bananas': 'many'}, mongo_dict)

    def test_to_dict_region(self):
        query = DatasetQuery(region=[11, -18, 12, -17.4])
        mongo_dict = self.converter.to_dict(query)
        self.assertEqual({'latitudes': {'$gte': -18, '$lte': -17.4},
                          'longitudes': {'$gte': 11, '$lte': 12}}, mongo_dict)

    def test_to_dict_times_start_to_stop(self):
        query = DatasetQuery(time=["2016-01-01T00:00:00", "2016-01-01T04:00:00"])
        mongo_dict = self.converter.to_dict(query)
        self.assertEqual({'times': {'$gte': datetime.datetime(2016, 1, 1, 0, 0),
                                    '$lte': datetime.datetime(2016, 1, 1, 4, 0)}}, mongo_dict)

    def test_to_dict_times_no_start(self):
        query = DatasetQuery(time=[None, "2016-01-01T04:00:00"])
        mongo_dict = self.converter.to_dict(query)
        self.assertEqual({'times': {'$lte': datetime.datetime(2016, 1, 1, 4, 0)}}, mongo_dict)

    def test_to_dict_times_no_stop(self):
        query = DatasetQuery(time=["2016-01-01T00:00:00", None])
        mongo_dict = self.converter.to_dict(query)
        self.assertEqual({'times': {'$gte': datetime.datetime(2016, 1, 1, 0, 0)}}, mongo_dict)

    def test_to_dict_both_None(self):
        query = DatasetQuery(time=[None, None])
        try:
            self.converter.to_dict(query)
            self.fail("ValueError expected")
        except ValueError:
            pass

    def test_to_dict_one_pgroup(self):
        query = DatasetQuery(pgroup=["sal"])

        mongo_dict = self.converter.to_dict(query)
        self.assertEqual({'attributes': {'$in': ['sal']}}, mongo_dict)

    def test_to_dict_two_pgroup(self):
        query = DatasetQuery(pgroup=["sal", "Chl"])

        mongo_dict = self.converter.to_dict(query)
        self.assertEqual({'attributes': {'$in': ['sal', 'Chl']}}, mongo_dict)

    def test_to_dict_shallow_no(self):
        query = DatasetQuery(shallow='no')

        mongo_dict = self.converter.to_dict(query)
        self.assertEqual({'metadata.optical_depth_warning': {'$not': {'$eq': 'true'}}}, mongo_dict)

    def test_to_dict_shallow_yes(self):
        query = DatasetQuery(shallow='yes')

        mongo_dict = self.converter.to_dict(query)
        self.assertEqual({}, mongo_dict)

    def test_to_dict_shallow_exclusively(self):
        query = DatasetQuery(shallow='exclusively')

        mongo_dict = self.converter.to_dict(query)
        self.assertEqual({'metadata.optical_depth_warning': 'true'}, mongo_dict)

    def test_to_dict_mtype_all(self):
        query = DatasetQuery(mtype='all')

        mongo_dict = self.converter.to_dict(query)
        self.assertEqual({}, mongo_dict)

    def test_to_dict_mtype_brdf(self):
        query = DatasetQuery(mtype='brdf')

        mongo_dict = self.converter.to_dict(query)
        self.assertEqual({'metadata.data_type': 'brdf'}, mongo_dict)
