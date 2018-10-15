# import os
import unittest

from eocdb.core.db.db_driver import DbDriver
from tests.ws.helpers import new_test_service_context


class WsContextTest(unittest.TestCase):
    def test_get_set_config(self):
        ctx = new_test_service_context()
        old_config = ctx.config
        new_config = dict(old_config)
        new_config.update(bibo=3567)
        ctx.configure(new_config)
        self.assertIsNot(new_config, ctx.config)
        self.assertEqual(new_config, ctx.config)

    def test_get_db_driver_with_default_test_config(self):
        ctx = new_test_service_context()
        driver = ctx.get_db_driver()
        self.assertIsInstance(driver, DbDriver)
        drivers = ctx.get_db_drivers()
        self.assertIsInstance(drivers, list)
        self.assertEqual(1, len(drivers))
        self.assertIs(driver, drivers[0])

    def test_get_db_driver_with_two_db_drivers_configured_and_another_not(self):
        ctx = new_test_service_context()
        ctx.configure({
            "databases": {
                "db_1": {
                    "type": "eocdb.db.mongo_db_driver.MongoDbDriver",
                    "primary": True,
                    "parameters": {
                        "mock": True,
                    }
                },
                "db_2": {
                    "type": "eocdb.db.mongo_db_driver.MongoDbDriver",
                    "parameters": {
                        "mock": True,
                    }
                },
            }
        })
        driver = ctx.get_db_driver()
        self.assertIsInstance(driver, DbDriver)
        drivers = ctx.get_db_drivers()
        self.assertIsInstance(drivers, list)
        self.assertEqual(2, len(drivers))
        self.assertIn(driver, drivers)

    def test_get_db_driver_with_no_db_drivers_configured(self):
        ctx = new_test_service_context()
        with self.assertRaises(RuntimeError) as cm:
            ctx.configure({"databases": {}})
            ctx.get_db_driver()
        self.assertEqual("No database driver found",
                         f"{cm.exception}")

    def test_get_db_driver_with_no_primary_db_driver_configured(self):
        ctx = new_test_service_context()
        with self.assertRaises(RuntimeError) as cm:
            ctx.configure({
                "databases": {
                    "db_1": {
                        "type": "eocdb.db.mongo_db_driver.MongoDbDriver",
                        "parameters": {
                            "mock": True,
                        }
                    },
                    "db_2": {
                        "type": "eocdb.db.mongo_db_driver.MongoDbDriver",
                        "parameters": {
                            "mock": True,
                        }
                    },
                }
            })
            ctx.get_db_driver()
        self.assertEqual("With multiple database drivers, one must be configured to be the primary one",
                         f"{cm.exception}")

    def test_get_db_driver_with_two_primary_db_drivers_configured(self):
        ctx = new_test_service_context()
        with self.assertRaises(RuntimeError) as cm:
            ctx.configure({
                "databases": {
                    "db_1": {
                        "type": "eocdb.db.mongo_db_driver.MongoDbDriver",
                        "primary": True,
                        "parameters": {
                            "mock": True,
                        }
                    },
                    "db_2": {
                        "type": "eocdb.db.mongo_db_driver.MongoDbDriver",
                        "primary": True,
                        "parameters": {
                            "mock": True,
                        }
                    },
                }
            })
            ctx.get_db_driver()
        self.assertEqual("There can only be a single primary database driver",
                         f"{cm.exception}")

