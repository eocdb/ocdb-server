from eocdb.db.mongo_db_driver import MongoDbDriver
from tests.db.test_mongo_db_driver import TestMongoDbDriver


class DbTestMongoDbDriver(TestMongoDbDriver):

    def setUp(self):
        self._driver = MongoDbDriver()
        self._driver.init()