from unittest import TestCase

from eocdb.core.models.dataset_ids import DatasetIds


class DatasetIdsTest(TestCase):

    def test_from_dict(self):
        id_dict = {"id_list": ["id_one", "id_two", "id_three", "id_four"], "docs": False}
        dataset_ids = DatasetIds.from_dict(id_dict)

        self.assertEqual(4, len(dataset_ids.id_list))
        self.assertEqual("id_three", dataset_ids.id_list[2])

        self.assertFalse(dataset_ids.docs)
