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
from ...db.static_data import get_groups_for_product

EOF = 'end_of_file'


class SbFileReader:

    def __init__(self):
        self._lines = []
        self._line_index = 0
        self._field_list = None

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

        delimiter_regex = self._extract_delimiter_regex(metadata)
        records = self._parse_records(delimiter_regex)

        # @Sabine: Folgende Änderungen habe ich durchgeführt, um den Bug ocdb-cli#37 zu lösen.
        #          "Explain inconsistency in number of fields, units and columns"
        #          Mein Ansatz:
        #          Es sollte erst geprüft werden, ob die Anzahl von Fields, Units und Columns
        #          identisch sind, bevor aus den beiden Spalte "date" und "time" der Zeitpunkt
        #          ausgelesen wird. Schließlich kann die Inkonsistenz in Fields, Units und
        #          Spaltenanzahl der Auslöser sein, warum die Zeit- oder Datumsangabe nicht in
        #          der richtigen Spalte steht und damit der Formattest nicht erfolgreich verläuft.
        #          Meine Annahmen:
        #          1. Ich gehe davon aus, dass der Submit-Vorgang, der über die die Web-UI durchgeführt
        #          wurde, abgebrochen wird, und unten links die Fehlermeldung erscheint.
        #          2. Auf dem CLI würde die Meldung entsprechend als Text ausgegeben.
        #
        #          Fortsetzung in _extract_date(cls, date_str, time_str, check_gmt=False).

        num_fields = len(metadata['fields'].split(','))
        len_record = len(records[0])

        if num_fields != len_record:
            raise SbFormatError('Number of fields (' + str(num_fields) + ') does not match ' +
                                'number of columns (' + str(len_record) + ').')

        if 'units' in metadata:
            num_units = len(metadata['units'].split(','))
            if num_fields != num_units:
                raise SbFormatError('Number of fields (' + str(num_fields) + ') does not match ' +
                                    'number of units (' + str(num_units) + ').')
        #     todo adapt unit level tests according to mandatory "units" field
        #     see: https://seabass.gsfc.nasa.gov/wiki/metadataheaders#units
        # else:
        #     raise SbFormatError('Field "units" of SeaBASS header not available.')

        dataset = DbDataset(metadata, records)
        dataset.attributes = self._extract_field_list()
        dataset.groups = self._extract_group_list()

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
                self._field_list = value

            metadata.update({key: value})

        return metadata

    def _extract_group_list(self):
        full_field_list = self._extract_field_list()
        group_list = []
        for field in full_field_list:
            groups = get_groups_for_product(field)
            if len(groups) == 0:
                continue

            for group in groups:
                if not group in group_list:
                    group_list.append(group)

        return group_list

    def _extract_field_list(self):
        if self._field_list is None:
            raise SbFormatError('Missing header tag "fields"')

        return self._field_list.lower().split(',')

    def _extract_searchfields(self, dataset):
        self._extract_geo_locations(dataset)
        self._extract_times(dataset)

    def _extract_times(self, dataset):
        # Check for '[GMT]' if start_time from Metadata is used,
        # otherwise use check_gmt=False.
        if 'date' in dataset.attribute_names and 'time' in dataset.attribute_names:
            # all time info in records as 'date' and 'time'
            date_index = dataset.attribute_names.index('date')
            time_index = dataset.attribute_names.index('time')
            for record in dataset.records:
                date_string = str(record[date_index])
                time_string = str(record[time_index])
                timestamp = self._extract_date(date_string, time_string, check_gmt=False)
                dataset.add_time(timestamp)
        # Year, month, day, hour, min and second defined per record
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
                timestamp = self._extract_date(start_date_string, time_string, check_gmt=False)
                dataset.add_time(timestamp)

        elif 'start_date' in dataset.metadata and 'start_time' in dataset.metadata:
            # time info solely in header
            start_date_string = dataset.metadata['start_date']
            start_time_string = dataset.metadata['start_time']
            timestamp = self._extract_date(start_date_string, start_time_string, check_gmt=True)
            # temporarily disabled, there are datasets in the SeaBASS excerpt that contain no time zone.
            # check docs if we allow for this .... tb 2018-09-20
            # timestamp = self._extract_date(start_date_string, start_time_string, check_gmt=True)
            dataset.add_time(timestamp)

        else:
            # Todo update to ocdb.readthedocs.io as soon as the website is repaired,
            #  i. e. the menu becomes visible.
            raise SbFormatError("Acquisition time not properly encoded. For details see: https://seabass.gsfc.nasa.gov/wiki/stdfields or https://seabass.gsfc.nasa.gov/wiki/metadataheaders#Example%20Header.")

    def _extract_geo_locations(self, dataset):
        if 'lon' in dataset.attribute_names and 'lat' in dataset.attribute_names:
            lon_index = dataset.attribute_names.index('lon')
            lat_index = dataset.attribute_names.index('lat')
            for record in dataset.records:
                lon = record[lon_index]
                lat = record[lat_index]
                dataset.add_geo_location(lon, lat)

        elif 'north_latitude' in dataset.metadata:
            self._extract_geo_location_from_header(dataset)

        else:
            raise SbFormatError("Geolocation not properly encoded")

    def _extract_geo_location_from_header(self, dataset):
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

    def _parse_records(self, delimiter_regex) -> List[List[Dataset.Field]]:
        records = []

        while True:
            line = self._next_line()
            if line == EOF:
                break
            if line == '\n':
                continue

            tokens = re.split(delimiter_regex, line)
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

        # Check time syntax in metadata (start_time)
        if check_gmt:
            # Check time syntax in metadata (start_time)
            if '[GMT]' not in time_str:
                raise SbFormatError("No time zone given. Required all times be expressed as [GMT]")

        if len(date_str) != 8:
            raise SbFormatError(f"Invalid date format ({date_str}). Format must correspond to YYYYMMDD.")

        try:
            year = int(date_str[0:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
        except Exception as e:
            raise SbFormatError(f"Invalid date format ({date_str}). Format must correspond to YYYYMMDD: {str(e)}")

        current_year = datetime.datetime.now().year
        if (not(1900 <= year <= current_year) or
                not(1 <= month <= 12) or
                not(1 <= day <= 31)):
            raise SbFormatError(f"Invalid date ({date_str}). Format corresponds to YYYYMMDD.\n" +
                                f"Valid value ranges for year month day are (1900-current_year) (1-12) (1-31)")

        if '[GMT]' in time_str:
            gmt_index = time_str.index('[GMT]')
            time_str = time_str[0:gmt_index]

        if not re.fullmatch('\d?\d:\d?\d:\d?\d', time_str):
            # todo really allow e.g. '2:18:4' instead of '02:18:04'
            # see: https://seabass.gsfc.nasa.gov/wiki/metadataheaders#start_date
            raise SbFormatError(f"Invalid time format ({time_str}). Format must correspond to HH:MM:SS.")

        tokens = time_str.split(':')

        try:
            hour = int(tokens[0])
            minute = int(tokens[1])
            second = int(tokens[2])
        except Exception as e:
            raise SbFormatError(f"Invalid time format ({time_str}). Format must correspond to HH:MM:SS: {str(e)}")

        if (not(0 <= hour < 24) or
            not(0 <= minute < 60) or
            not(0 <= second < 60)):
            raise SbFormatError(f"Invalid time format ({time_str}).\n"
                                f"Valid value ranges for HH MM SS are (0-23) (0-59) (0-59)")

        try:
            return datetime.datetime(year, month, day, hour, minute, second)
        except Exception as e:
            date_time_str = date_str + ' ' + time_str
            raise SbFormatError(f"Invalid date or time format ({date_time_str}): {str(e)}")

# noinspection PyArgumentList
class SbFormatError(Exception):
    """
    This error is raised if SbFileReader encounters format errors.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
