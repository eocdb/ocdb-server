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

        dataset.records = [[109.8, -38.4, 998, 20, 36],
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

    def test_get_offset_only(self):
        self._add_test_datasets_to_db()

        query = DatasetQuery(offset=1)
        result = self._driver.find_datasets(query)
        self.assertEqual(10, result.total_count)
        self.assertEqual("dataset-0", result.datasets[0].name)

        query = DatasetQuery(offset=2)
        result = self._driver.find_datasets(query)
        self.assertEqual(9, result.total_count)
        self.assertEqual("dataset-1", result.datasets[0].name)

        query = DatasetQuery(offset=6)
        result = self._driver.find_datasets(query)
        self.assertEqual(5, result.total_count)
        self.assertEqual("dataset-5", result.datasets[0].name)

    def test_get_count_only(self):
        self._add_test_datasets_to_db()

        query = DatasetQuery(count=4)
        result = self._driver.find_datasets(query)
        self.assertEqual(10, result.total_count)
        self.assertEqual("dataset-0", result.datasets[0].name)

        query = DatasetQuery(count=7)
        result = self._driver.find_datasets(query)
        self.assertEqual(10, result.total_count)
        self.assertEqual("dataset-0", result.datasets[0].name)

    def test_get_count_zero_returns_number_of_results(self):
        self._add_test_datasets_to_db()

        query = DatasetQuery(count=0)
        result = self._driver.find_datasets(query)
        self.assertEqual(10, result.total_count)
        self.assertEqual([], result.datasets)

    def test_get_offset_and_count(self):
        self._add_test_datasets_to_db()

        query = DatasetQuery(offset=2, count=4)
        result = self._driver.find_datasets(query)
        self.assertEqual(9, result.total_count)
        self.assertEqual("dataset-1", result.datasets[0].name)

        query = DatasetQuery(offset=5, count=3)
        result = self._driver.find_datasets(query)
        self.assertEqual(6, result.total_count)
        self.assertEqual("dataset-4", result.datasets[0].name)

        query = DatasetQuery(offset=8, count=5)
        result = self._driver.find_datasets(query)
        self.assertEqual(3, result.total_count)
        self.assertEqual("dataset-7", result.datasets[0].name)

    def test_get_offset_and_negative_count(self):
        self._add_test_datasets_to_db()

        query = DatasetQuery(offset=1, count=-1)
        result = self._driver.find_datasets(query)
        self.assertEqual(10, result.total_count)
        self.assertEqual("dataset-0", result.datasets[0].name)
        self.assertEqual("dataset-9", result.datasets[9].name)

        query = DatasetQuery(offset=4, count=-1)
        result = self._driver.find_datasets(query)
        self.assertEqual(7, result.total_count)
        self.assertEqual("dataset-3", result.datasets[0].name)

    def test_insert_two_and_get_by_location(self):
        dataset = helpers.new_test_db_dataset(11)
        dataset.add_geo_location(lon=-76.3461, lat=39.0652)
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(12)
        dataset.add_geo_location(lon=-76.4373, lat=38.7354)
        self._driver.add_dataset(dataset)

        query = DatasetQuery(region=[-77.0, 38.0, -76.0, 38.9])  # covers second dataset tb 2018-10-23

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("dataset-12", result.datasets[0].name)

    def test_insert_two_and_get_by_location_many_records(self):
        dataset = helpers.new_test_db_dataset(13)
        dataset.add_geo_location(lon=-69.8150, lat=42.7250)
        dataset.add_geo_location(lon=-69.8167, lat=42.7158)
        dataset.add_geo_location(lon=-69.7675, lat=43.1685)
        dataset.add_geo_location(lon=-70.2030, lat=43.1400)
        dataset.add_geo_location(lon=-70.2053, lat=42.5045)
        dataset.add_geo_location(lon=-69.5458, lat=42.7790)
        dataset.add_geo_location(lon=-69.1059, lat=42.5036)
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(14)
        dataset.add_geo_location(lon=-158.750, lat=20.421)
        dataset.add_geo_location(lon=-160.182, lat=18.892)
        dataset.add_geo_location(lon=-161.317, lat=17.672)
        dataset.add_geo_location(lon=-163.296, lat=15.519)
        self._driver.add_dataset(dataset)

        query = DatasetQuery(region=[-71.0, 43.0, -70.0, 43.5])  # covers first dataset tb 2018-10-24

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("dataset-13", result.datasets[0].name)

    def test_insert_two_and_get_by_location_and_metadata(self):
        dataset = helpers.new_test_db_dataset(15)
        dataset.metadata["data_status"] = "final"
        dataset.add_geo_location(lon=82, lat=-10)
        dataset.add_geo_location(lon=82.5, lat=-10.3)
        dataset.add_geo_location(lon=82.8, lat=-10.19)
        self._driver.add_dataset(dataset)

        dataset = helpers.new_test_db_dataset(16)
        dataset.metadata["data_status"] = "test"
        dataset.add_geo_location(lon=16.8, lat=-72.34)
        dataset.add_geo_location(lon=16.7, lat=-71.98)
        dataset.add_geo_location(lon=16.69, lat=-72.11)
        self._driver.add_dataset(dataset)

        query = DatasetQuery(expr='data_status: test', region=[15.0, -75.0, 17.0, -70.0])  # covers second dataset tb 2018-10-24

        result = self._driver.find_datasets(query)
        self.assertEqual(1, result.total_count)
        self.assertEqual("dataset-16", result.datasets[0].name)

        query = DatasetQuery(expr='data_status: test', region=[25.0, -75.0, 27.0, -70.0])  # region does not match tb 2018-10-24

        result = self._driver.find_datasets(query)
        self.assertEqual(0, result.total_count)

        query = DatasetQuery(expr='data_status: experimental', region=[15.0, -75.0, 17.0, -70.0])  # status does not match tb 2018-10-24

        result = self._driver.find_datasets(query)
        self.assertEqual(0, result.total_count)

    def test_get_get_start_index_and_page_size(self):
        query = DatasetQuery()
        query.offset = 1
        self.assertEqual((0, 1000), self._driver._get_start_index_and_count(query))

        query.offset = 12
        query.count = 106
        self.assertEqual((11, 106), self._driver._get_start_index_and_count(query))

        query.offset = 14
        query.count = None
        self.assertEqual((13, 0), self._driver._get_start_index_and_count(query))

    def test_get_get_start_index_and_page_size_raises_on_offset_zero(self):
        query = DatasetQuery()
        query.offset = 0

        try:
            self._driver._get_start_index_and_count(query)
            self.fail("ValueError expected")
        except ValueError:
            pass

    def test_get_get_start_index_and_negative_page_size(self):
        query = DatasetQuery()
        query.offset = 1
        query.count = -1
        self.assertEqual((0, 0), self._driver._get_start_index_and_count(query))

    def test_to_dataset_ref(self):
        dataset_dict = {"_id": "nasenmann.org", "name": "Rosamunde", "path": "/where/is/your/mama/gone"}

        dataset_ref = self._driver._to_dataset_ref(dataset_dict)
        self.assertEqual("nasenmann.org", dataset_ref.id)
        self.assertEqual("Rosamunde", dataset_ref.name)
        self.assertEqual("/where/is/your/mama/gone", dataset_ref.path)

    def _add_test_datasets_to_db(self):
        for i in range(0, 10):
            dataset = helpers.new_test_dataset(i)
            self._driver.add_dataset(dataset)
