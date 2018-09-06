import unittest

from eocdb.db.sqlite_test_db_driver import SQLiteTestDbDriver


class TestSQLiteTestDbDriver(unittest.TestCase):

    def setUp(self):
        self.driver = SQLiteTestDbDriver()
        self.driver.connect()

    def tearDown(self):
        self.driver.close()

    def test_fetch_ernie_data(self):
        dataset = self.driver.get("ernie")

        self.assertEqual(5, dataset.record_count)
        self.assertAlmostEqual(58.1, dataset.records[0][0], 8)
        self.assertAlmostEqual(11.1, dataset.records[0][1], 8)

        self.assertAlmostEqual(58.5, dataset.records[2][0], 8)
        self.assertAlmostEqual(10.9, dataset.records[2][1], 8)

        self.assertEqual(3, dataset.attribute_count)
        self.assertEqual(['lon', 'lat', 'chl'], dataset.attribute_names)

    def test_fetch_bert_data(self):
        dataset = self.driver.get("Bert")

        self.assertEqual(0, dataset.record_count)

    # def test_insert_and_fetch(self):
    #     self.driver.insert("Bibo", "I'm the new guy")
    #
    #     dataset = self.driver.get("Bibo")
    #     self.assertEqual(1, dataset.record_count)
    #     # self.assertEqual(2, results[0][0][0])  # id
    #     # self.assertEqual("Bibo", results[0][0][1])  # name
    #     # self.assertEqual("I'm the new guy", results[0][0][2])  # description
