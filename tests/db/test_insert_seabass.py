import os
import unittest

from tests.db.insert_seabass import create_relative_path


class InsertSeabassTest(unittest.TestCase):

    def test_create_relative_path(self):
        archive_path = os.path.abspath('/usr/local/oc-db/data/seabass_extract')
        doc_path = os.path.abspath('/usr/local/oc-db/data/seabass_extract/NASA_GSFC/ECOMON/archive/aop/tst_file.csv')

        relative_path = create_relative_path(archive_path, doc_path)
        self.assertTrue(str(relative_path).startswith('NASA'))
        self.assertEqual("tst_file.csv", relative_path.name)