from datetime import datetime
from unittest import TestCase

from eocdb.core.time_helper import TimeHelper


class TimeHelperTest(TestCase):

    def test_parse_time(self):
        self.assertEqual(datetime(2008, 7, 11, 0, 0), TimeHelper.parse_datetime("2008-07-11"))
        self.assertEqual(datetime(2009, 8, 12, 11, 22, 41), TimeHelper.parse_datetime("2009-08-12T11:22:41"))