# The MIT License (MIT)
# Copyright (c) 2018 by EUMETSAT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import unittest

from eocdb.core.models.issue import Issue
from eocdb.ws.controllers.datasets import *
from ..helpers import new_test_service_context, new_dataset


class DatasetsTest(unittest.TestCase):

    def setUp(self):
        self.ctx = new_test_service_context()

    def test_validate_dataset(self):
        dataset = new_dataset(11)
        dataset.id = None
        result = validate_dataset(self.ctx, dataset=dataset)
        expected_result = DatasetValidationResult("OK", [])
        self.assertEqual(expected_result, result)

        dataset = new_dataset(11)
        dataset.id = "Grunz"
        result = validate_dataset(self.ctx, dataset=dataset)
        issue = Issue("WARNING", "Datasets should have no ID before insert or update")
        expected_result = DatasetValidationResult("WARNING", [issue])
        self.assertEqual(expected_result, result)

    def test_add_dataset(self):
        add_dataset(self.ctx, dataset=new_dataset(1))
        add_dataset(self.ctx, dataset=new_dataset(2))

    def test_find_datasets(self):
        add_dataset(self.ctx, dataset=new_dataset(1))
        add_dataset(self.ctx, dataset=new_dataset(2))
        add_dataset(self.ctx, dataset=new_dataset(3))

        expr = None
        region = None
        time = None
        wdepth = None
        mtype = "all"
        wlmode = "all"
        shallow = "no"
        pmode = 'contains'
        pgroup = None
        pname = None
        offset = None
        count = None

        # noinspection PyTypeChecker
        result = find_datasets(self.ctx,
                               expr=expr,
                               region=region,
                               time=time,
                               wdepth=wdepth,
                               mtype=mtype,
                               wlmode=wlmode,
                               shallow=shallow,
                               pmode=pmode,
                               pgroup=pgroup,
                               pname=pname,
                               offset=offset,
                               count=count)

        self.assertIsInstance(result, DatasetQueryResult)
        self.assertEqual(3, result.total_count)

    def test_get_dataset_by_id(self):
        add_dataset(self.ctx, dataset=new_dataset(1))
        add_dataset(self.ctx, dataset=new_dataset(2))
        add_dataset(self.ctx, dataset=new_dataset(3))
        result = find_datasets(self.ctx)
        dataset_id_1 = result.datasets[0].id
        dataset_id_2 = result.datasets[1].id
        dataset_id_3 = result.datasets[2].id
        dataset_1 = get_dataset_by_id(self.ctx, dataset_id_1)
        self.assertIsNotNone(dataset_1)
        self.assertEqual(dataset_id_1, dataset_1.id)
        dataset_2 = get_dataset_by_id(self.ctx, dataset_id_2)
        self.assertIsNotNone(dataset_2)
        self.assertEqual(dataset_id_2, dataset_2.id)
        dataset_3 = get_dataset_by_id(self.ctx, dataset_id_3)
        self.assertIsNotNone(dataset_3)
        self.assertEqual(dataset_id_3, dataset_3.id)
        with self.assertRaises(WsResourceNotFoundError):
            get_dataset_by_id(self.ctx, "gnarz")

    @unittest.skip('not implemented yet')
    def test_update_dataset(self):
        # noinspection PyArgumentList
        dataset = Dataset()
        # TODO (generated): set data properties
        result = update_dataset(self.ctx, dataset=dataset)
        self.assertIsNone(result)

    @unittest.skip('not implemented yet')
    def test_delete_dataset(self):
        # TODO (generated): set required parameters
        dataset_id = None
        # TODO (generated): set optional parameters
        api_key = None
        # noinspection PyArgumentList
        result = delete_dataset(self.ctx, dataset_id, api_key=api_key)
        self.assertIsNone(result)

    @unittest.skip('not implemented yet')
    def test_get_datasets_in_bucket(self):
        # TODO (generated): set required parameters
        affil = None
        project = None
        cruise = None
        # noinspection PyTypeChecker
        result = get_datasets_in_bucket(self.ctx, affil, project, cruise)
        self.assertIsInstance(result, list)
        # TODO (generated): set expected result
        expected_result = []
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_get_dataset_by_bucket_and_name(self):
        # TODO (generated): set required parameters
        affil = None
        project = None
        cruise = None
        name = None
        # noinspection PyTypeChecker
        result = get_dataset_by_bucket_and_name(self.ctx, affil, project, cruise, name)
        # TODO (generated): set expected result
        expected_result = None
        self.assertEqual(expected_result, result)
