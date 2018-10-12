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

from eocdb.ws.controllers.users import *
from eocdb.core.models.api_response import ApiResponse
from eocdb.core.models.user import User
from ..helpers import new_test_service_context


class UsersTest(unittest.TestCase):

    def setUp(self):
        self.ctx = new_test_service_context()

    @unittest.skip('not implemented yet')
    def test_create_user(self):
        data = User()
        # TODO: set data properties

        result = create_user(self.ctx, data=data)
        self.assertIsInstance(result, ApiResponse)
        expected_result = ApiResponse()
        # TODO: set expected result properties
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_login_user(self):
        # TODO: set optional parameters
        username = None
        password = None

        result = login_user(self.ctx, username=username, password=password)
        # TODO: set expected result
        expected_result = None
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_logout_user(self):
        result = logout_user(self.ctx)
        self.assertIsInstance(result, ApiResponse)
        expected_result = ApiResponse()
        # TODO: set expected result properties
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_get_user_by_id(self):
        # TODO: set required parameters
        id_ = None

        result = get_user_by_id(self.ctx, id_)
        self.assertIsInstance(result, User)
        expected_result = User()
        # TODO: set expected result properties
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_update_user(self):
        # TODO: set required parameters
        id_ = None
        data = User()
        # TODO: set data properties

        result = update_user(self.ctx, id_, data=data)
        self.assertIsInstance(result, ApiResponse)
        expected_result = ApiResponse()
        # TODO: set expected result properties
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_delete_user(self):
        # TODO: set required parameters
        id_ = None

        result = delete_user(self.ctx, id_)
        self.assertIsInstance(result, ApiResponse)
        expected_result = ApiResponse()
        # TODO: set expected result properties
        self.assertEqual(expected_result, result)
