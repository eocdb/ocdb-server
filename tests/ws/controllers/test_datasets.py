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

from eocdb.ws.controllers.datasets import *
from eocdb.core.models.api_response import ApiResponse
from eocdb.core.models.dataset import Dataset
from eocdb.core.models.dataset_query_result import DatasetQueryResult
from eocdb.core.models.dataset_validation_result import DatasetValidationResult
from ..helpers import new_test_service_context


class DatasetsTest(unittest.TestCase):

    def setUp(self):
        self.ctx = new_test_service_context()

    @unittest.skip('not implemented yet')
    def test_find_datasets(self):
        # TODO: set optional parameters
        expr = None
        region = None
        time = None
        wdepth = None
        mtype = None
        wlmode = None
        shallow = None
        pmode = None
        pgroup = None
        pname = None
        offset = None
        count = None

        result = find_datasets(self.ctx, expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype, wlmode=wlmode,
                               shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname, offset=offset, count=count)
        self.assertIsInstance(result, DatasetQueryResult)
        expected_result = DatasetQueryResult()
        # TODO: set expected result properties
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_add_dataset(self):
        data = Dataset()
        # TODO: set data properties
        # TODO: set optional parameters
        dry = None

        result = add_dataset(self.ctx, data=data, dry=dry)
        self.assertIsInstance(result, DatasetValidationResult)
        expected_result = DatasetValidationResult()
        # TODO: set expected result properties
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_update_dataset(self):
        data = Dataset()
        # TODO: set data properties
        # TODO: set optional parameters
        dry = None

        result = update_dataset(self.ctx, data=data, dry=dry)
        self.assertIsInstance(result, ApiResponse)
        expected_result = ApiResponse()
        # TODO: set expected result properties
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_get_dataset_by_id(self):
        # TODO: set required parameters
        id_ = None

        result = get_dataset_by_id(self.ctx, id_)
        self.assertIsInstance(result, Dataset)
        expected_result = Dataset()
        # TODO: set expected result properties
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_delete_dataset(self):
        # TODO: set required parameters
        id_ = None
        # TODO: set optional parameters
        api_key = None

        result = delete_dataset(self.ctx, id_, api_key=api_key)
        self.assertIsInstance(result, ApiResponse)
        expected_result = ApiResponse()
        # TODO: set expected result properties
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_get_datasets_in_bucket(self):
        # TODO: set required parameters
        affil = None
        project = None
        cruise = None

        result = get_datasets_in_bucket(self.ctx, affil, project, cruise)
        self.assertIsInstance(result, list)
        # TODO: set expected result
        expected_result = []
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_get_dataset_by_bucket_and_name(self):
        # TODO: set required parameters
        affil = None
        project = None
        cruise = None
        name = None

        result = get_dataset_by_bucket_and_name(self.ctx, affil, project, cruise, name)
        # TODO: set expected result
        expected_result = None
        self.assertEqual(expected_result, result)
