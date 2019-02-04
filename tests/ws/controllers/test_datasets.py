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
from eocdb.core.models.qc_info import QC_INFO_STATUS_ONGOING, QC_INFO_STATUS_PASSED
from eocdb.ws.controllers.datasets import *
from tests.helpers import new_test_service_context, new_test_dataset


class DatasetsTest(unittest.TestCase):

    def setUp(self):
        self.ctx = new_test_service_context()

    def test_validate_dataset(self):
        dataset = new_test_dataset(11)
        dataset.id = None
        result = validate_dataset(self.ctx, dataset=dataset)
        expected_result = DatasetValidationResult("OK", [])
        self.assertEqual(expected_result, result)

        dataset = new_test_dataset(11)
        dataset.id = "Grunz"
        result = validate_dataset(self.ctx, dataset=dataset)
        issue = Issue("WARNING", "Datasets should have no ID before insert or update")
        expected_result = DatasetValidationResult("WARNING", [issue])
        self.assertEqual(expected_result, result)

    def test_add_dataset(self):
        dataset_1 = new_test_dataset(6)
        result_1 = add_dataset(self.ctx, dataset=dataset_1)
        self.assertIsInstance(result_1, DatasetRef)
        self.assertIsNotNone(result_1.id)
        self.assertEqual(dataset_1.path, result_1.path)

        dataset_2 = new_test_dataset(8)
        result_2 = add_dataset(self.ctx, dataset=dataset_2)
        self.assertIsInstance(result_2, DatasetRef)
        self.assertIsNotNone(result_2.id)
        self.assertNotEqual(result_1.id, result_2.id)
        self.assertEqual(dataset_2.path, result_2.path)

    def test_find_datasets_default_parameter(self):
        add_dataset(self.ctx, dataset=new_test_dataset(1))
        add_dataset(self.ctx, dataset=new_test_dataset(2))
        add_dataset(self.ctx, dataset=new_test_dataset(3))

        expr = None
        region = None
        time = None
        wdepth = None
        mtype = None
        wlmode = 'all'
        shallow = 'no'
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

    def test_find_datasets_pgroup(self):
        dataset = new_test_dataset(1)
        dataset.attributes = ["a"]
        add_dataset(self.ctx, dataset=dataset)

        dataset = new_test_dataset(2)
        dataset.attributes = ["sal"]
        add_dataset(self.ctx, dataset=dataset)

        dataset = new_test_dataset(3)
        dataset.attributes = ["Chl_a", "Chl_b"]
        add_dataset(self.ctx, dataset=dataset)

        expr = None
        region = None
        time = None
        wdepth = None
        mtype = None
        wlmode = 'all'
        shallow = 'no'
        pmode = 'contains'
        pgroup = ['sal']
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
        self.assertEqual(1, result.total_count)

    def test_find_datasets_with_geolocations(self):
        dataset = new_test_dataset(1)
        dataset.longitudes = [104, 105]
        dataset.latitudes = [22, 23]
        add_dataset(self.ctx, dataset=dataset)

        dataset = new_test_dataset(2)
        dataset.longitudes = [114, 115]
        dataset.latitudes = [32, 33]
        add_dataset(self.ctx, dataset=dataset)

        dataset = new_test_dataset(3)
        dataset.longitudes = [124, 125]
        dataset.latitudes = [42, 43]
        add_dataset(self.ctx, dataset=dataset)

        expr = None
        region = [110, 30, 120, 35]
        time = None
        wdepth = None
        mtype = None
        wlmode = 'all'
        shallow = 'no'
        pmode = 'contains'
        pgroup = None
        pname = None
        offset = None
        count = None
        geojson = True

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
                               count=count,
                               geojson=geojson)

        self.assertIsInstance(result, DatasetQueryResult)
        self.assertEqual(1, result.total_count)
        self.assertEqual(1, len(result.locations))
        ds_id = result.datasets[0].id
        self.assertEqual("{'type':'FeatureCollection','features':["
                         "{'type':'Feature','geometry':{'type':'Point','coordinates':[114,32]}},"
                         "{'type':'Feature','geometry':{'type':'Point','coordinates':[115,33]}}]}",
                         result.locations[ds_id])

    def test_get_dataset_by_id(self):
        dataset_id_1 = add_dataset(self.ctx, dataset=new_test_dataset(1)).id
        dataset_id_2 = add_dataset(self.ctx, dataset=new_test_dataset(2)).id
        dataset_id_3 = add_dataset(self.ctx, dataset=new_test_dataset(3)).id
        dataset_1 = get_dataset_by_id_strict(self.ctx, dataset_id_1)
        self.assertIsNotNone(dataset_1)
        self.assertEqual(dataset_id_1, dataset_1.id)
        dataset_2 = get_dataset_by_id_strict(self.ctx, dataset_id_2)
        self.assertIsNotNone(dataset_2)
        self.assertEqual(dataset_id_2, dataset_2.id)
        dataset_3 = get_dataset_by_id_strict(self.ctx, dataset_id_3)
        self.assertIsNotNone(dataset_3)
        self.assertEqual(dataset_id_3, dataset_3.id)
        with self.assertRaises(WsResourceNotFoundError):
            get_dataset_by_id_strict(self.ctx, "gnarz")

    def test_update_dataset(self):
        dataset_ref = add_dataset(self.ctx, new_test_dataset(42))
        dataset_id = dataset_ref.id
        dataset_update = new_test_dataset(42)
        dataset_update.id = dataset_id
        dataset_update.path = "a/b/c/archive/x/x-01.csv"
        update_dataset(self.ctx, dataset=dataset_update)
        updated_dataset = get_dataset_by_id_strict(self.ctx, dataset_id)
        self.assertEqual(dataset_update, updated_dataset)

    def test_delete_dataset(self):
        dataset_ref = add_dataset(self.ctx, new_test_dataset(42))
        dataset_id = dataset_ref.id
        dataset = get_dataset_by_id_strict(self.ctx, dataset_id)
        self.assertEqual(dataset_id, dataset.id)
        delete_dataset(self.ctx, "api_key", dataset_id)
        with self.assertRaises(WsResourceNotFoundError):
            delete_dataset(self.ctx, "api_key", dataset_id)

    @unittest.skip('not implemented yet')
    def test_get_datasets_in_path(self):
        # TODO (generated): set required parameters
        affil = None
        project = None
        cruise = None
        # noinspection PyTypeChecker
        result = get_datasets_in_path(self.ctx, affil, project, cruise)
        self.assertIsInstance(result, list)
        # TODO (generated): set expected result
        expected_result = []
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_get_dataset_by_name(self):
        # TODO (generated): set required parameters
        affil = None
        project = None
        cruise = None
        name = None
        # noinspection PyTypeChecker
        result = get_dataset_by_name(self.ctx, affil, project, cruise, name)
        # TODO (generated): set expected result
        expected_result = None
        self.assertEqual(expected_result, result)

    def test_get_set_dataset_qc_info(self):
        dataset_ref = add_dataset(self.ctx, new_test_dataset(42))
        dataset_id = dataset_ref.id

        qc_info = get_dataset_qc_info(self.ctx, dataset_id)
        self.assertEqual(QcInfo(QC_INFO_STATUS_WAITING), qc_info)

        expected_qc_info = QcInfo(QC_INFO_STATUS_ONGOING)
        set_dataset_qc_info(self.ctx, dataset_id, expected_qc_info)
        qc_info = get_dataset_qc_info(self.ctx, dataset_id)
        self.assertEqual(expected_qc_info, qc_info)

        expected_qc_info = QcInfo(QC_INFO_STATUS_PASSED,
                                  dict(by='Illaria',
                                       when="2019-02-01",
                                       doc_files=["qc-report.docx"]))
        set_dataset_qc_info(self.ctx, dataset_id, expected_qc_info)
        qc_info = get_dataset_qc_info(self.ctx, dataset_id)
        self.assertEqual(expected_qc_info, qc_info)
