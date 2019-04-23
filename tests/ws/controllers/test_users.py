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
from tests.helpers import new_test_service_context


class UsersTest(unittest.TestCase):

    def setUp(self):
        self.ctx = new_test_service_context()

    @unittest.skip('TODO: Fix THIS')
    def test_login_user(self):
        # noinspection PyTypeChecker
        result = login_user(self.ctx, username="scott", password="tiger")
        expected_result = {
            'id': 1,
            'name': 'scott',
            'email': 'bruce.scott@gmail.com',
            'first_name': 'Bruce',
            'last_name': 'Scott',
            'phone': '+34 5678901234',
            'roles': ['submit', 'admin']
        }
        self.assertEqual(expected_result, result)

        result = login_user(self.ctx, username="bruce.scott@gmail.com", password="tiger")
        expected_result = {
            'id': 1,
            'name': 'scott',
            'email': 'bruce.scott@gmail.com',
            'first_name': 'Bruce',
            'last_name': 'Scott',
            'phone': '+34 5678901234',
            'roles': ['submit', 'admin']
        }
        self.assertEqual(expected_result, result)

        with self.assertRaises(WsUnauthorizedError) as cm:
            login_user(self.ctx, username="scott", password="lion")
        self.assertEqual("HTTP 401: Unknown username or password", f"{cm.exception}")

        with self.assertRaises(WsUnauthorizedError) as cm:
            login_user(self.ctx, username="bibo", password="tiger")
        self.assertEqual("HTTP 401: Unknown username or password", f"{cm.exception}")

    @unittest.skip('not implemented yet')
    def test_create_user(self):
        # noinspection PyArgumentList
        user = User()
        # TODO (generated):  data properties
        # noinspection PyArgumentList
        result = create_user(self.ctx, user=user)
        self.assertIsNone(result)

    @unittest.skip('not implemented yet')
    def test_logout_user(self):
        result = logout_user(self.ctx)
        self.assertIsNone(result)

    @unittest.skip('not implemented yet')
    def test_get_user_by_id(self):
        # TODO (generated): set required parameters
        user_id = -1
        result = get_user_by_id(self.ctx, user_id)
        self.assertIsInstance(result, User)
        # noinspection PyArgumentList
        expected_result = User()
        # TODO (generated): set expected result properties
        self.assertEqual(expected_result, result)

    @unittest.skip('not implemented yet')
    def test_update_user(self):
        # TODO (generated): set required parameters
        user_id = -1
        # noinspection PyArgumentList
        data = User()
        # TODO (generated): set data properties

        result = update_user(self.ctx, user_id, data=data)
        self.assertIsNone(result)

    @unittest.skip('not implemented yet')
    def test_delete_user(self):
        # TODO (generated): set required parameters
        user_id = -1
        result = delete_user(self.ctx, user_id)
        self.assertIsNone(result)
