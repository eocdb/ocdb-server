import unittest

from eocdb.ws.controllers.links import get_links, update_links
from tests.helpers import new_test_service_context


class LinksTest(unittest.TestCase):

    def setUp(self):
        self.ctx = new_test_service_context()

    def test_get_links(self):
        result = get_links(self.ctx)
        self.assertEqual(result, "## Links")

    def test_update_links(self):
        update_links(self.ctx, "# Links")
        result = get_links(self.ctx)
        self.assertEqual(result, "# Links")
        update_links(self.ctx, "## Links")
