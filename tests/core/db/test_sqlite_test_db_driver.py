import unittest

from eocdb.core.db.sqlite_test_db_driver import SQLiteTestDbDriver


class TestSQLiteTestDbDriver(unittest.TestCase):

    def setUp(self):
        self.driver = SQLiteTestDbDriver()
        self.driver.connect()

    def tearDown(self):
        self.driver.close()

    def test_fetch_ernie_data(self):
        results = self.driver.get("Ernie")

        self.assertEqual(1, len(results))
        self.assertEqual("Ernie", results[0][0])
        self.assertEqual("I am your favourite result", results[0][1])

    def test_fetch_bert_data(self):
        results = self.driver.get("Bert")

        self.assertEqual(0, len(results))

    def test_insert_and_fetch(self):
        self.driver.insert("Bibo", "I'm the new guy")

        results = self.driver.get("Bibo")
        self.assertEqual(1, len(results))
        self.assertEqual("Bibo", results[0][0])
        self.assertEqual("I'm the new guy", results[0][1])
