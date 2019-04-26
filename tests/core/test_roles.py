import unittest

from eocdb.core.roles import Roles


class RolesTest(unittest.TestCase):

    def test_entries(self):
        self.assertEqual(2, len(Roles.__members__))

        self.assertEqual("admin", Roles.ADMIN.value)
        self.assertEqual("submit", Roles.SUBMIT.value)

    def test_is_admin(self):
        roles = ['submit', 'admin']
        self.assertTrue(Roles.is_admin(roles))