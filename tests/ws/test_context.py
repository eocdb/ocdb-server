# import os
import os
import unittest
from datetime import datetime

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
        path = ctx.store_path
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.eocdb/store"))

    def test_upload_path(self):
        ctx = new_test_service_context()
        path = ctx.upload_path
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.eocdb/uploads"))

    def test_get_datasets_store_path(self):
        ctx = new_test_service_context()
        path = ctx.get_datasets_store_path("BIGELOW/BALCH/gnats")
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.eocdb/store/BIGELOW/BALCH/gnats/archive"))

    def test_get_doc_files_store_path(self):
        ctx = new_test_service_context()
        path = ctx.get_doc_files_store_path("BIGELOW/BALCH/gnats")
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.eocdb/store/BIGELOW/BALCH/gnats/documents"))

    def test_get_datasets_upload_path(self):
        ctx = new_test_service_context()
        path = ctx.get_datasets_upload_path("INPE/Ubatuba")
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.eocdb/uploads/INPE/Ubatuba/archive"))

    def test_get_doc_files_upload_path(self):
        ctx = new_test_service_context()
        path = ctx.get_doc_files_upload_path("INPE/Ubatuba")
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.eocdb/uploads/INPE/Ubatuba/documents"))

    def test_db_driver(self):
        ctx = new_test_service_context()
        self.assertIsInstance(ctx.db_driver, DbDriver)

    def test_get_db_drivers(self):
        ctx = new_test_service_context()
        self.assertIsInstance(ctx.db_drivers, list)
