# import os
import unittest

from tests.helpers import new_test_service_context


class WsContextTest(unittest.TestCase):
    def test_get_set_config(self):
        ctx = new_test_service_context()
        old_config = ctx.config
        new_config = dict(old_config)
        new_config.update(bibo=3567)
        ctx.configure(new_config)
        self.assertIsNot(new_config, ctx.config)
        self.assertEqual(new_config, ctx.config)