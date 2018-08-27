import unittest

from eocdb.core.db.sqlite_test_db_driver import SQLiteTestDbDriver


class TestSQLiteTestDbDriver(unittest.TestCase):

    def setUp(self):
        self.driver = SQLiteTestDbDriver()
        self.driver.connect()

    def tearDown(self):
        self.driver.close()

    def test_fetch_ernie_data(self):
        results = self.driver.get("ernie")

        self.assertEqual(1, len(results))
        self.assertEqual(1, results[0][0][0])
        self.assertEqual("ernie", results[0][0][1])
        self.assertEqual("I am your favourite result", results[0][0][2])

    def test_fetch_bert_data(self):
        results = self.driver.get("Bert")

        self.assertEqual(0, len(results))

    def test_insert_and_fetch(self):
        self.driver.insert("Bibo", "I'm the new guy")

        results = self.driver.get("Bibo")
        self.assertEqual(1, len(results))
        self.assertEqual(2, results[0][0][0])  # id
        self.assertEqual("Bibo", results[0][0][1])  # name
        self.assertEqual("I'm the new guy", results[0][0][2])  # description
