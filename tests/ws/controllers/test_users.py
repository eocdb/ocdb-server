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

from ocdb.core.db.db_user import DbUser
from ocdb.core.roles import Roles
from ocdb.ws.controllers.users import *
from tests.helpers import new_test_service_context


class UsersTest(unittest.TestCase):

    def setUp(self):
        self.ctx = new_test_service_context()

    def test_login_user(self):
        user = User(name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                    first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

        create_user(self.ctx, user)
        # noinspection PyTypeChecker
        result = login_user(self.ctx, username="scott", password="tiger")

        result['id'] = ''

        expected_result = {
            'id': '',
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

    def test_create_user(self):
        # noinspection PyArgumentList
        user = User(name='tom2', last_name='Scott', password='hh', email='email@email.int',
                    first_name='Tom', roles=[Roles.ADMIN.value], phone='02102238958')

        result = create_user(self.ctx, user=user)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    def test_get_user_by_name(self):
        user = User(name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                    first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

        create_user(self.ctx, user)

        result = get_user_by_name(self.ctx, 'scott')
        result['id'] = ''
        expected_result = {
            'id': '',
            'name': 'scott',
            'email': 'bruce.scott@gmail.com',
            'first_name': 'Bruce',
            'last_name': 'Scott',
            'phone': '+34 5678901234',
            'roles': ['submit', 'admin']
        }

        self.assertEqual(expected_result, result)

    def test_update_user(self):
        user = DbUser(id_='tt', name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                      first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

        create_user(self.ctx, user)

        result = update_user(self.ctx, 'scott', data={'name': 'Tom'})
        self.assertIs(result, True)

    def test_delete_user(self):
        user = User(name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                    first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

        create_user(self.ctx, user)

        with self.assertRaises(WsBadRequestError) as cm:
            delete_user(self.ctx, user_name="god")

        self.assertEqual("HTTP 400: Could not delete user god", f"{cm.exception}")

        result = delete_user(self.ctx, 'scott')
        self.assertIs(result, True)
