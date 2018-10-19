import unittest

from eocdb.core.db.errors import OperationalError
from eocdb.core.models.dataset import DATASET_STATUS_NEW, DATASET_STATUS_VALIDATING
from eocdb.core.models.dataset_query import DatasetQuery
from eocdb.db.mongo_db_driver import MongoDbDriver
from tests import helpers


class TestMongoDbDriver(unittest.TestCase):

    def setUp(self):
        self._driver = MongoDbDriver()
        self._driver.init(mock=True)

    def tearDown(self):
        self._driver.clear()
        self._driver.close()

    def test_connect_twice_throws(self):
        try:
            self._driver.connect()
            self.fail("OperationalError expected")
        except OperationalError:
            pass

    def test_insert_one_and_get(self):
        dataset = helpers.new_test_dataset(1)
        dataset.metadata["affiliations"] = "UCSB"
        dataset.metadata["received"] = "20160829"
        dataset.metadata["investigators"] = "Norm_Nelson"

        dataset.records = [[109.8,  -38.4, 998, 20, 36],
                           [109.9, -38.3, 998, 20, 35]]

        ds_id = self._driver.add_dataset(dataset)

        result = self._driver.get_dataset(ds_id)
        self.assertIsNotNone(result)
        self.assertEqual("UCSB", result.metadata["affiliations"])
        self.assertEqual("Norm_Nelson", result.metadata["investigators"])
        self.assertEqual(2, len(result.records))
        self.assertAlmostEqual(109.8, result.records[0][0], 8)
        self.assertAlmostEqual(-38.3, result.records[1][1], 8)

    def test_get_invalid_id(self):
        dataset = helpers.new_test_dataset(2)

        self._driver.add_dataset(dataset)

        result = self._driver.get_dataset("rippelschnatz")
        self.assertIsNone(result)

    # noinspection PyTypeChecker
    def test_get_null_id(self):
        result = self._driver.get_dataset(None)
        self.assertIsNone(result)

    def test_insert_two_and_get_empty_expression(self):
        dataset = helpers.new_test_dataset(1)
        dataset.metadata["source"] = "we_don_t_care"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(2)
        dataset.metadata["source"] = "we_want_this"
        self._driver.add_dataset(dataset)

        result = self._driver.find_datasets(DatasetQuery())
        self.assertEqual(2, result.total_count)

    def test_insert_two_and_get_by_metadata_field(self):
        dataset = helpers.new_test_dataset(3)
        dataset.metadata["source"] = "we_don_t_care"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(4)
        dataset.metadata["source"] = "we_want_this"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="source: we_want_this")

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("dataset-4", result.datasets[0].name)

    def test_insert_three_and_get_by_metadata_field_and(self):
        dataset = helpers.new_test_dataset(3)
        dataset.metadata["affiliations"] = "we_don_t_care"
        dataset.metadata["cruise"] = "baltic_1"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(4)
        dataset.metadata["affiliations"] = "we_want_this"
        dataset.metadata["cruise"] = "baltic_2"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(5)
        dataset.metadata["affiliations"] = "we_want_this"
        dataset.metadata["cruise"] = "baltic_1"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="affiliations: we_want_this AND cruise: baltic_1")

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("dataset-5", result.datasets[0].name)

        query = DatasetQuery(expr="affiliations: we_want_this AND cruise: baltic_2")

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("dataset-4", result.datasets[0].name)

    def test_insert_three_and_get_by_metadata_field_or(self):
        dataset = helpers.new_test_dataset(6)
        dataset.metadata["affiliations"] = "we_don_t_care"
        dataset.metadata["cruise"] = "baltic_1"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(7)
        dataset.metadata["affiliations"] = "we_want_this"
        dataset.metadata["cruise"] = "baltic_2"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(8)
        dataset.metadata["affiliations"] = "we_want_this"
        dataset.metadata["cruise"] = "baltic_1"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="affiliations: we_want_this OR cruise: baltic_1")

        result = self._driver.find_datasets(query)
        self.assertEqual(3, result.total_count)
        self.assertEqual("dataset-6", result.datasets[0].name)

        query = DatasetQuery(expr="affiliations: we_want_this OR cruise: baltic_2")

        result = self._driver.find_datasets(query)
        self.assertEqual(2, result.total_count)
        self.assertEqual("dataset-7", result.datasets[0].name)

    def test_insert_and_get_by_not_existing_metadata_field(self):
        dataset = helpers.new_test_dataset(9)
        dataset.metadata["calibration_files"] = "yes_they_are_here"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="the_absent_field: not_there")
        result = self._driver.find_datasets(query)
        self.assertEqual(0, result.total_count)

    def test_insert_and_get_by_path(self):
        dataset = helpers.new_test_dataset(9)
        dataset.path = "/usr/local/path/schnath"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(10)
        dataset.path = "C:\\data\\seabass\\cruise"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="path: /usr/local/path/schnath")

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("dataset-9", result.datasets[0].name)

    def test_insert_and_get_by_name(self):
        dataset = helpers.new_test_dataset(11)
        dataset.name = "Helga"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(12)
        dataset.name = "Gertrud"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="name: Gertrud")

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("Gertrud", result.datasets[0].name)

    def test_insert_and_get_by_name_single_char_wildcard(self):
        dataset = helpers.new_test_dataset(13)
        dataset.name = "Helga"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(14)
        dataset.name = "Helma"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(15)
        dataset.name = "Olga"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="name: Hel?a")

        result = self._driver.find_datasets(query)
        self.assertEqual(2, result.total_count)
        self.assertEqual("Helga", result.datasets[0].name)
        self.assertEqual("Helma", result.datasets[1].name)

    def test_insert_and_get_by_name_multi_char_wildcard(self):
        dataset = helpers.new_test_dataset(13)
        dataset.name = "Helga"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(14)
        dataset.name = "Helma"
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(15)
        dataset.name = "Olga"
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="name: *ga")

        result = self._driver.find_datasets(query)
        self.assertEqual(2, result.total_count)
        self.assertEqual("Helga", result.datasets[0].name)
        self.assertEqual("Olga", result.datasets[1].name)

    def test_insert_and_get_by_status(self):
        dataset = helpers.new_test_dataset(13)
        dataset.status = DATASET_STATUS_NEW
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_dataset(14)
        dataset.status = DATASET_STATUS_VALIDATING
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr="status: validating")

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("dataset-14", result.datasets[0].name)

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

    def test_get_get_start_index_and_page_size(self):
        query = DatasetQuery()
        query.offset = 1
        self.assertEqual((0, 1000), self._driver._get_start_index_and_page_size(query))

        query.offset = 12
        query.count = 106
        self.assertEqual((11, 106), self._driver._get_start_index_and_page_size(query))

        query.offset = 14
        query.count = None
        self.assertEqual((13, -1), self._driver._get_start_index_and_page_size(query))

    def test_get_get_start_index_and_page_size_raises_on_offset_zero(self):
        query = DatasetQuery()
        query.offset = 0

        try:
            self._driver._get_start_index_and_page_size(query)
            self.fail("ValueError expected")
        except ValueError:
            pass
