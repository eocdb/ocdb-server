import unittest

from eocdb.core.db.mongo_db_driver import MongoDbDriver


class TestMongoDbDriver(unittest.TestCase):

    def setUp(self):
        self.driver = MongoDbDriver()
        self.driver.connect()

    def tearDown(self):
        # @todo 1 tb/tb this hangs!!! check why and resolve 2018-08-31
        self.driver.clear()
        self.driver.close()

    def test_connect_twice_throws(self):
        try:
            self.driver.connect()
            self.fail("Exception expected")
        except:
            pass

    def test_insert_one_and_get(self):
        doc = {"affiliations" : "UCSB",
               "received" : 20160829,
               "investigators": "Norm_Nelson",
               "records" : [{"lon" : 109.8, "lat" : -38.4, "station" : 998, "depth" : 20, "sample" : 36},
                            {"lon": 109.8, "lat": -38.4, "station": 998, "depth": 20, "sample": 35}]}

        self.driver.insert(doc)

        dataset_list = self.driver.get()
        self.assertEqual(1, len(dataset_list))
        self.assertEqual("UCSB", dataset_list[0].metadata["affiliations"])
