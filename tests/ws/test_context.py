# import os
import unittest

from eocdb.core.db.db_driver import DbDriver
from tests.helpers import new_test_service_context


class WsContextTest(unittest.TestCase):

    def test_get_set_config(self):
        ctx = new_test_service_context()
        old_config = ctx.config
        new_config = dict(old_config)
        new_config.update(bibo=3567)
        ctx.configure(new_config)
        self.assertIsNot(new_config, ctx.config)
        self.assertEqual(new_config, ctx.config)

    def test_base_dir(self):
        ctx = new_test_service_context()
        self.assertIsInstance(ctx.base_dir, str)
        self.assertTrue(ctx.base_dir.replace("\\", "/").endswith("/eocdb-server/tests/ws/res"))

    def test_store_path(self):
        ctx = new_test_service_context()
        self.assertIsInstance(ctx.store_path, str)
        self.assertTrue(ctx.store_path.replace("\\", "/").endswith("/.eocdb/store"))

    def test_db_driver(self):
        ctx = new_test_service_context()
        self.assertIsInstance(ctx.db_driver, DbDriver)

    def test_get_db_drivers(self):
        ctx = new_test_service_context()
        self.assertIsInstance(ctx.db_drivers, list)
