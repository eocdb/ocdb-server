# import os
import unittest

from ocdb.core.db.db_driver import DbDriver
from ocdb.core.db.db_user import DbUser
from ocdb.core.roles import Roles
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
        self.assertTrue(ctx.base_dir.replace("\\", "/").endswith("/ocdb-server/tests/ws/res"))

    def test_store_path(self):
        ctx = new_test_service_context()
        path = ctx.store_path
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.ocdb/store"))

    def test_upload_path(self):
        ctx = new_test_service_context()
        path = ctx.upload_path
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.ocdb/store"))

    def test_get_datasets_store_path(self):
        ctx = new_test_service_context()
        path = ctx.get_datasets_store_path("BIGELOW/BALCH/gnats")
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.ocdb/store/BIGELOW/BALCH/gnats/archive"))

    def test_get_doc_files_store_path(self):
        ctx = new_test_service_context()
        path = ctx.get_doc_files_store_path("BIGELOW/BALCH/gnats")
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.ocdb/store/BIGELOW/BALCH/gnats/documents"))

    def test_get_datasets_upload_path(self):
        ctx = new_test_service_context()
        path = ctx.get_datasets_upload_path("INPE/Ubatuba")
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.ocdb/store/INPE/Ubatuba/archive"))

    def test_get_doc_files_upload_path(self):
        ctx = new_test_service_context()
        path = ctx.get_doc_files_upload_path("INPE/Ubatuba")
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.ocdb/store/INPE/Ubatuba/documents"))

    def test_submission_path(self):
        ctx = new_test_service_context()
        path = ctx.get_submission_path("LAVAL_U/babin/ICESCAPE")
        self.assertIsInstance(path, str)
        self.assertTrue(path.replace("\\", "/").endswith("/.ocdb/store/LAVAL_U/babin/ICESCAPE"))

    def test_db_driver(self):
        ctx = new_test_service_context()
        self.assertIsInstance(ctx.db_driver, DbDriver)

    def test_get_db_drivers(self):
        ctx = new_test_service_context()
        self.assertIsInstance(ctx.db_drivers, list)

    def test_get_user_none_present(self):
        ctx = new_test_service_context()
        user = ctx.get_user("walter")
        self.assertIsNone(user)

        user = ctx.get_user("fritz", "geheim!")
        self.assertIsNone(user)

    def test_get_user_from_DB(self):
        ctx = new_test_service_context()

        user_stored = DbUser(id_='asodvia', name='tom', last_name='Scott', password='hh', email='email@email.int',
                      first_name='Tom', roles=[Roles.ADMIN.value], phone='02102238958')
        ctx.db_driver.add_user(user_stored)

        user = ctx.get_user("tom")
        self.assertIsNotNone(user)
        self.assertEqual("Scott", user.last_name)

        user = ctx.get_user("tom", "hh")
        self.assertIsNotNone(user)
        self.assertEqual("email@email.int", user.email)

    def test_get_user_from_DB_wrong_password(self):
        ctx = new_test_service_context()

        user_stored = DbUser(id_='asodvia', name='tom', last_name='Scott', password='hh', email='email@email.int',
                             first_name='Tom', roles=[Roles.ADMIN.value], phone='02102238958')
        ctx.db_driver.add_user(user_stored)

        user = ctx.get_user("tom", "incorrect_pwd")
        self.assertIsNone(user)

    def test_get_user_admin_user_empty_db(self):
        ctx = new_test_service_context()

        user = ctx.get_user("chef")
        self.assertIsNotNone(user)

        user = ctx.get_user("chef", "eocdb_chef")
        self.assertIsNotNone(user)

    def test_get_user_admin_user_empty_db_wrong_password(self):
        ctx = new_test_service_context()

        user = ctx.get_user("chef", "completely_wrong")
        self.assertIsNone(user)

    def test_get_user_admin_user_filled_db(self):
        ctx = new_test_service_context()

        user_stored = DbUser(id_='asodvia', name='tom', last_name='Scott', password='hh', email='email@email.int',
                             first_name='Tom', roles=[Roles.ADMIN.value], phone='02102238958')
        ctx.db_driver.add_user(user_stored)

        user = ctx.get_user("chef")
        self.assertIsNotNone(user)

        user = ctx.get_user("chef", "eocdb_chef")
        self.assertIsNotNone(user)



