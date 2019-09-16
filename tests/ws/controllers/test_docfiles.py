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

from ocdb.ws.controllers.docfiles import *
from tests.helpers import new_test_service_context


class DocFilesTest(unittest.TestCase):

    def setUp(self):
        self.ctx = new_test_service_context()

    @unittest.skip('not implemented yet')
    def test_add_doc_file(self):
        # TODO (generated): set data dict items
        data = {}

        result = add_doc_file(self.ctx, data=data)
        self.assertIsNone(result)

    @unittest.skip('not implemented yet')
    def test_update_doc_file(self):
        # TODO (generated): set data dict items
        data = {}

        result = update_doc_file(self.ctx, data=data)
        self.assertIsNone(result)

    @unittest.skip('not implemented yet')
    def test_get_doc_files_in_bucket(self):
        # TODO (generated): set required parameters
        affil = None
        project = None
        cruise = None

        # noinspection PyTypeChecker
        result = get_doc_files_in_path(self.ctx, affil, project, cruise)
        self.assertIsInstance(result, list)
        # TODO (generated): set expected result
        expected_result = []
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_download_doc_file(self):
        # TODO (generated): set required parameters
        affil = None
        project = None
        cruise = None
        name = None

        # noinspection PyTypeChecker
        result = get_doc_file_by_name(self.ctx, affil, project, cruise, name)
        # TODO (generated): set expected result
        expected_result = None
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_delete_doc_file(self):
        # TODO (generated): set required parameters
        affil = None
        project = None
        cruise = None
        name = None

        # noinspection PyTypeChecker
        result = delete_doc_file(self.ctx, affil, project, cruise, name)
        self.assertIsNone(result)
