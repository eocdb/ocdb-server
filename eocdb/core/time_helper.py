from datetime import datetime

import numpy as np


class TimeHelper:

    @staticmethod
    def parse_datetime(time_string) -> datetime:
        """ Parses a date/time string in format YYYY-MM-DDThh:mm:ss to a UTC datetime object"""
        np_datetime = np.datetime64(time_string)
        ts = (np_datetime - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')
        return datetime.utcfromtimestamp(ts)
