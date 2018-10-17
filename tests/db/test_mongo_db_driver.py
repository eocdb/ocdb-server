import unittest

from eocdb.core.query.parser import QueryParser
from eocdb.db.mongo_db_driver import MongoDbDriver
from tests import helpers


class TestMongoDbDriver(unittest.TestCase):

    def setUp(self):
        self.driver = MongoDbDriver()
        self.driver.init(mock=True)

    def tearDown(self):
        self.driver.clear()
        self.driver.close()

    def test_connect_twice_throws(self):
        try:
            self.driver.connect()
            self.fail("Exception expected")
        except:
            pass

    def test_insert_one_and_get(self):
        dataset = helpers.new_test_dataset(1)
        dataset.metadata["affiliations"] = "UCSB"
        dataset.metadata["received"] = "20160829"
        dataset.metadata["investigators"] = "Norm_Nelson"

        dataset.records = [{"lon": 109.8, "lat": -38.4, "station": 998, "depth": 20, "sample": 36},
                           {"lon": 109.8, "lat": -38.4, "station": 998, "depth": 20, "sample": 35}]

        id = self.driver.add_dataset(dataset)

        result = self.driver.get_dataset(id)
        self.assertIsNotNone(result)

    def test_insert_two_and_get_by_location(self):
        pass
        # doc = {"affiliations": "UCSB",
        #        "received": 20160829,
        #        "investigators": "Norm_Nelson",
        #        "records": [{"lon": 109.7, "lat": -38.3, "station": 998, "depth": 20, "sample": 36},
        #                    {"lon": 109.9, "lat": -38.5, "station": 998, "depth": 20, "sample": 35}]}
        #
        # self.driver.insert(doc)
        #
        # doc = {"affiliations": "Laboratoire_Optique_Atmospherique",
        #        "received": 20020321,
        #        "investigators": "Pierre_Yves_Deschamps",
        #        "records": [{"lon": -122.26, "lat": 30.52, "SZA": 44.62, "pressure_atm": -9, "wind": -9},
        #                    {"lon": -122.26, "lat": 30.52, "SZA": 39.11, "pressure_atm": -9, "wind": -9}]}
        #
        # self.driver.insert(doc)
        #
        # dataset_list = self.driver.get()
        # self.assertEqual(2, len(dataset_list))
        #
        # P = QueryParser
        # expression = P.parse("lon:[107 TO 110] AND lat:[-40 TO -35]")
        #
        # dataset_list = self.driver.get(expression)
        # self.assertEqual(1, len(dataset_list))
        # self.assertEqual("UCSB", dataset_list[0].metadata["affiliations"])
        #
        # expression = P.parse("lon:[-125 TO -120] AND lat:[29 TO 31]")
        # dataset_list = self.driver.get(expression)
        # self.assertEqual(1, len(dataset_list))
        # self.assertEqual("Laboratoire_Optique_Atmospherique", dataset_list[0].metadata["affiliations"])
