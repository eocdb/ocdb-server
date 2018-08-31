import unittest

from eocdb.core.db.mongo_db_driver import MongoDbDriver


class TestMongoDbDriver(unittest.TestCase):

    def setUp(self):
        self.driver = MongoDbDriver()
        self.driver.connect()

    def tearDown(self):
        # @todo 1 tb/tb this hangs!!! check why and resolve 2018-08-31
        #self.driver.clear()
        self.driver.close()

    def test_connect_twice_throws(self):
        try:
            self.driver.connect()
            self.fail("Exception expected")
        except:
            pass

    def test_insert_and_get(self):
        pass
