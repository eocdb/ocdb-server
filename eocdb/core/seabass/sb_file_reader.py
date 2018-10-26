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

import datetime
import re
from typing import List, Sequence, Any

from ..db.db_dataset import DbDataset
from ..models.dataset import Dataset

EOF = 'end_of_file'


class SbFileReader:

    def __init__(self):
        self._lines = []
        self._line_index = 0

    def read(self, file_obj: Any) -> Dataset:
        """
        Read a Dataset from plain text file in SeaBASS format.

        :param file_obj: A path or a file-like object.
        :return: A Dataset
        """
        self._line_index = 0
        if hasattr(file_obj, "readlines"):
            return self._parse(file_obj.readlines())
        else:
            with open(file_obj, 'r') as fp:
                return self._parse(fp.readlines())

    def _parse(self, lines: Sequence[str]) -> DbDataset:

        self._lines = lines

        self.handle_header = None

        metadata = {}
        line = self._next_line()
        if '/begin_header' in line.lower():
            self.handle_header = True
            metadata = self._parse_header()

        field_list = self._extract_field_list(metadata)
        records = self._parse_records()
        dataset = DbDataset(metadata, records)
        dataset.set_attributes(field_list)
        self._extract_searchfields(dataset)

        if self.handle_header is None or self.handle_header is True:
            raise SbFormatError("/end_header tag missing")

        return dataset

    def _next_line(self) -> str:
        if self._line_index < len(self._lines):
            line = self._lines[self._line_index]
            self._line_index += 1
            return line

        return EOF

    def _parse_header(self) -> dict:
        metadata = dict()
        while True:
            line = self._next_line()
            if line == EOF:
                break

            # strip comments
            if line.startswith('!'):
                continue

            # done with header
            if '/end_header' in line.lower():
                if self.handle_header:
                    self.handle_header = False
                    break
                else:
                    raise IOError("/end_header tag found without /begin_header")

            # split line, trim and remove leading slash
            line = re.sub("[\r\n]+", '', line).strip()
            if '=' not in line:
                # then it is no key/value pair - skip this line tb 2018-09-20
                continue

            [key, value] = line.split('=', 1)
            key = key[1:].strip()
            value = value.strip()
            if key == 'fields':
                self.field_list = value
            else:
                metadata.update({key: value})

        return metadata

    def _extract_field_list(self, metadata):
        self._delimiter_regex = self._extract_delimiter_regex(metadata)

        if self.field_list is None:
            raise SbFormatError('Missing header tag "fields"')

        return self.field_list.lower().split(',')

    def _extract_searchfields(self, dataset):
        self._extract_geo_locations(dataset)
        self._extract_times(dataset)

    def _extract_times(self, dataset):
        if 'date' in dataset.attribute_names and 'time' in dataset.attribute_names:
            # all time info in records as 'date' and 'time'
            date_index = dataset.attribute_names.index('date')
            time_index = dataset.attribute_names.index('time')
            for record in dataset.records:
                date_string = str(record[date_index])
                time_string = str(record[time_index])
                timestamp = self._extract_date(date_string, time_string)
                dataset.add_time(timestamp)

        elif 'year' in dataset.attribute_names and 'hour' in dataset.attribute_names:
            year_index = dataset.attribute_names.index('year')
            month_index = dataset.attribute_names.index('month')
            day_index = dataset.attribute_names.index('day')
            hour_index = dataset.attribute_names.index('hour')
            minute_index = dataset.attribute_names.index('minute')
            second_index = -1
            if 'second' in dataset.attribute_names:
                second_index = dataset.attribute_names.index('second')

            for record in dataset.records:
                year = record[year_index]
                month = record[month_index]
                day = record[day_index]
                hour = record[hour_index]
                minute = record[minute_index]
                second = 0
                if second_index >= 0:
                    second = record[second_index]
                dataset.add_time(datetime.datetime(year, month, day, hour, minute, second))

        elif 'date' not in dataset.attribute_names and 'time' in dataset.attribute_names:
            # time information split into header and record part
            start_date_string = dataset.metadata['start_date']
            time_index = dataset.attribute_names.index('time')
            for record in dataset.records:
                time_string = str(record[time_index])
                timestamp = self._extract_date(start_date_string, time_string)
                dataset.add_time(timestamp)

        elif 'start_date' in dataset.metadata:
            # time info solely in header
            start_date_string = dataset.metadata['start_date']
            start_time_string = dataset.metadata['start_time']
            timestamp = self._extract_date(start_date_string, start_time_string, check_gmt=False)
            # temporarily disabled, there are datasets in the SeaBASS excerpt that contain no time zone.
            # check docs if we allow for this .... tb 2018-09-20
            # timestamp = self._extract_date(start_date_string, start_time_string, check_gmt=True)
            dataset.add_time(timestamp)

        else:
            raise SbFormatError("Acquisition time not properly encoded")

    def _extract_geo_locations(self, dataset):
        if 'lon' in dataset.attribute_names and 'lat' in dataset.attribute_names:
            lon_index = dataset.attribute_names.index('lon')
            lat_index = dataset.attribute_names.index('lat')
            for record in dataset.records:
                lon = record[lon_index]
                lat = record[lat_index]
                dataset.add_geo_location(lon, lat)

        elif 'north_latitude' in dataset.metadata:
            self._extract_geo_location_form_header(dataset)

        else:
            raise SbFormatError("Geolocation not properly encoded")

    def _extract_geo_location_form_header(self, dataset):
        east_lon_string = dataset.metadata['east_longitude']
        lon = self._extract_angle(east_lon_string)
        north_lat_string = dataset.metadata['north_latitude']
        lat = self._extract_angle(north_lat_string)
        dataset.add_geo_location(lon, lat)

    @classmethod
    def extract_value_if_present(cls, key, metadata):
        if key in metadata:
            return metadata[key]
        else:
            return "n_a"

    def _parse_records(self) -> List[List[Dataset.Field]]:
        records = []

        while True:
            line = self._next_line()
            if line == EOF:
                break

            tokens = re.split(self._delimiter_regex, line)
            if len(tokens) <= 1:
                # some files have whitespace between header and records - skip this here tb 2018-09-21
                continue

            record = []
            for token in tokens:
                if len(token) < 1:
                    continue

                if self._is_number(token):
                    if self._is_integer(token):
                        record.append(int(token))
                    else:
                        record.append(float(token))
                else:
                    record.append(token)

            records.append(record)

        return records

    @classmethod
    def _extract_delimiter_regex(cls, metadata):
        if 'delimiter' not in metadata:
            raise SbFormatError('Missing delimiter tag in header')

        delimiter = metadata['delimiter']
        if delimiter == 'comma':
            return ',+'
        elif delimiter == 'space':
            return '\s+'
        elif delimiter == 'tab':
            return '\t+'
        else:
            raise SbFormatError('Invalid delimiter-value in header')

    @classmethod
    def _is_number(cls, token):
        try:
            float(token)
            return True
        except ValueError:
            return False

    @classmethod
    def _is_integer(cls, token):
        try:
            int(token)
            return True
        except ValueError:
            return False

    @classmethod
    def _extract_angle(cls, angle_str):
        parse_str = angle_str
        if '[' in angle_str:
            unit_index = parse_str.find('[')
            parse_str = angle_str[0:unit_index]
        return float(parse_str)

    @classmethod
    def _extract_date(cls, date_str, time_str, check_gmt=False):
        time_str = time_str.upper()
        if check_gmt:
            if '[GMT]' not in time_str:
                raise SbFormatError("No time zone given. Required all times be expressed as [GMT]")

        year = int(date_str[0:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])

        if '[GMT]' in time_str:
            gmt_index = time_str.index('[GMT]')
            time_str = time_str[0:gmt_index]

        tokens = time_str.split(':')
        hour = int(tokens[0])
        minute = int(tokens[1])
        second = int(tokens[2])

        return datetime.datetime(year, month, day, hour, minute, second)


class SbFormatError(Exception):
    """
    This error is raised if SbFileReader encounters format errors.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
