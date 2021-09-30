# Created: 2021-09-21
# MOBY reader based on SEABASS reader

__author__ = 'UweL'

import os
import datetime
import re
import statistics

from typing import List, Sequence, Any

import numpy as np

from ..db.db_dataset import DbDataset
from ..models.dataset import Dataset
from ...db.static_data import get_groups_for_product

EOF = 'end_of_file'


class MobyFileReader:

    def __init__(self, fn):
        self._delimiter = ','
        self._lines = []
        self._line_index = 0
        self._field_list = None
        self._filename = fn

    def read(self, file_obj: Any) -> Dataset:
        """
        Read a Dataset from plain text file in MOBY format.

        :param file_obj: A path or a file-like object.
        :return: A Dataset
        """
        self._line_index = 0
        self._filename = file_obj

        if hasattr(file_obj, 'readlines'):
            return self._parse(file_obj.readlines())
        else:
            with open(file_obj, 'r') as fp:
                return self._parse(fp.readlines())

    def _check_line_for_filename(self, str_line):
        """Check whether string contains filename:

        :param str_line:
        :return: True, if string contains filename.
        """
        # Check for "File:"
        str_line = str_line.strip()
        if str_line[0:5] != 'File:':
            err_msg = 'First line does not correspond to pattern ' + \
                      '"File: [Filename]"'
            raise MobyFormatError(err_msg)
        # Check for filename
        file, ext = os.path.splitext(os.path.basename(self._filename))
        if file[5:] + '.mby' not in str_line.lower():
            err_msg = 'First line does not contain filename'
            raise MobyFormatError(err_msg)

        return True

    def _parse(self, lines: Sequence[str]) -> DbDataset:

        self._lines = lines

        self.handle_header = None

        metadata = {}
        line = self._next_line()

        # 2.1 Check filename
        contains_fn = self._check_line_for_filename(line)
        if contains_fn is True:
            self.handle_header = True
            self.metadata = self._parse_header()

        # delimiter_regex = self._extract_delimiter_regex(metadata)
        delimiter_regex = self._delimiter    # + '+'
        records = self._parse_records(delimiter_regex)
        dataset = DbDataset(self.metadata, records)
        
        dataset.attributes = self._extract_field_list()
        # Todo: Add groups for MOBY attributes/fields.
        dataset.groups = self._extract_group_list()
        self._extract_searchfields(dataset, metadata)

        if self.handle_header is None or self.handle_header is True:
            raise MobyFormatError('Parsing error')

        return dataset

    def _parse_records(self, delimiter_regex) -> List[List[Dataset.Field]]:
        records = []

        while True:
            line = self._next_line()

            if line == EOF:
                break
            if line == '\n':
                continue
            line = " ".join(line.split()).replace(' ', '')
            tokens = re.split(delimiter_regex, line)
            if len(tokens) <= 1:
                # some files have whitespace between header and records -
                # skip this here tb 2018-09-21
                continue

            record = []
            for token in tokens:
                if len(token) < 1:
                    record.append(np.nan)
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

    def _current_line(self) -> str:
        # Line index corresponds to the line pointer, i. e. next line
        line = self._lines[self._line_index - 1].strip()
        return line

    def _next_line(self) -> str:
        line = ''
        if self._line_index < len(self._lines):
            while line == '':
                line = self._lines[self._line_index]
                line = re.sub("[\r\n]+", '', line).strip()
                self._line_index += 1
                if self._line_index == len(self._lines):
                    break

            return line

        return EOF

    def _get_num_vars_and_data(self, str_line):
        """Get number of variables and data rows

        :param str_line:
        :return: number of variables and data rows
        """
        var_and_points = str_line.split(' ')
        # print(var_and_points)
        if (len(var_and_points) != 5 or
                var_and_points[1] != 'Variables' or
                var_and_points[3] != 'Data' or
                var_and_points[4] != 'Points'):
            err_msg = 'Check variables and points line'
            raise MobyFormatError(err_msg)

        n_variables = int(var_and_points[0])
        n_data_rows = int(var_and_points[2])

        return n_variables, n_data_rows

    def _get_comment_lines(self, start_str):
        """Collect all lines starting with start_str as comments:

        :param line:
        :param comments:
        :param start_str:
        :return: line
        """
        comments = []
        if start_str == '##':
            comments.append(['! Processing comments:'])
        elif start_str == 'DscS':
            comments.append(['! DscS comments:'])
        elif start_str == 'FhdS':
            comments.append(['! FhdS comments:'])
        else:
            print('Start string is unknown!')
            raise MobyFormatError

        line = self._next_line()
        while line.find(start_str) == 0:
            if start_str == 'DscS':
                if (line.find('Water-Leaving Radiance') > -1 and
                        line.find('(µW/cm²/sr/nm)') == -1):
                    print(self._filename + ': Wrong unit for LW in line: ' +
                          line + '.')
                    exit(-1)
                if (line.find(': Surface Irradiance') > -1 and
                        line.find('(µW/cm²/nm)') == -1):
                    print(self._filename + ': Wrong unit for LW in line: ' +
                          line + '.')
                    exit(-1)

            comments.append('! ' + line.replace('##', ''))
            line = self._next_line()

        if len(comments) == 1:
            raise MobyFormatError(start_str + ' comments missing.')

        return comments

    def _collect_metadata_column_names(self):
        """
        :param str_col_names:
        :return:
        """

        date_time_columns = ['Year', 'Mon', 'Day', 'Hour', 'Min', 'Sec']
        str_col_names = self._next_line()
        str_col_names = " ".join(str_col_names.split())
        col_names = str_col_names.split(' ')
        if col_names[0:6] != date_time_columns:
            err_msg = 'Date and time columns missing in metadata columns, ' + \
                  'i. e. Year, Mon, Day, Hour, Min, Sec.'
            raise MobyFormatError(err_msg)

        return col_names

    def _collect_metadata_units(self):
        """Collect units for metadata columns.
        :param line:
        :return:
        """
        str_units = self._next_line()
        str_units = str_units.replace('(', '')
        str_units = str_units.replace(')', '')
        str_units = str_units.replace('deg True', 'deg_True')
        str_units = " ".join(str_units.split())
        metadata_units = ['', '', '', '', '', ''] + str_units.split(' ')

        return metadata_units

    def _collect_lw_ids(self):
        """Collect all lines for Lw:

        :return: lw_ids, lw_values:
        """
        lw_ids = []
        lw_values = []
        lw_values_list = []
        line = self._next_line()
        if line[0:2] != 'LW':
            line = self._next_line()
        while line[0:2] == 'LW':

            lw_id = int(line[2:4].replace(':', ''))
            str_lw_values = line[5:].strip()
            str_lw_values = " ".join(str_lw_values.split())
            lw_values = str_lw_values.split(' ')
            lw_values_list.append(lw_values)

            lw_ids.append(lw_id)
            line = self._next_line()

        return lw_ids, lw_values_list

    def _collect_es_ids(self):

        """Collect all lines for Es:

        :return: es_ids, es_values
        """
        es_ids = []
        es_values_list = []
        line = self._current_line()
        while line[0:2] == 'ES':

            es_id = int(line[9:10].replace(':', ''))
            str_es_values = line[11:].strip()
            str_es_values = " ".join(str_es_values.split())
            es_values = str_es_values.split(' ')
            es_values_list.append(es_values)

            es_ids.append(es_id)
            line = self._next_line()

        return es_ids, es_values_list

    def _parse_header(self) -> dict:

        metadata = {}

        line = self._next_line()

        # 2.2 Variables and points
        line = line.replace(',', '')
        num_vars, num_rows = self._get_num_vars_and_data(line)
        metadata['num_vars'] = num_vars
        metadata['num_rows'] = num_rows

        # 2.3 File headers
        comment_lines = self._get_comment_lines('FhdS')

        metadata['comments'] = comment_lines

        # 2.4 Metadata block
        if self._current_line() != 'META DATA:':
            msg = 'Metadata tag missing.'
            raise MobyFormatError(msg)

        # 2.5 Metadata columns
        metadata_columns = self._collect_metadata_column_names()
        metadata['columns'] = metadata_columns

        # 2.6 Metadata units
        metadata_units = self._collect_metadata_units()
        metadata['units'] = metadata_units

        # 2.7 LWs
        lw_ids, lw_values = self._collect_lw_ids()
        metadata['lw_ids'] = lw_ids
        metadata['lw_values'] = lw_values

        # 2.8 ESs
        es_ids, es_values = self._collect_es_ids()
        metadata['es_ids'] = es_ids
        metadata['es_values'] = es_values

        if len(lw_ids) != len(es_ids):
            raise IOError('Different number of ids for lw and es:' +
                          str(lw_ids) + ', ' + str(es_ids))

        # 2.9 Other comments
        processing_comments = self._get_comment_lines('##')
        metadata['processing_comments'] = processing_comments

        dscs_comments = self._get_comment_lines('DscS')
        metadata['dscs_comments'] = dscs_comments

        # Done with header
        if 'xdat:' in self._current_line().lower():
            # Todo: Wird diese Fallunterscheidung benötigt?
            if self.handle_header:
                line = self._next_line()
                # Todo: Add index for "Ed Sfc" columns
                lw_ids = metadata['lw_ids']
                for lw_id in lw_ids:
                    line = line.replace(str('Ed Sfc'), 'Es' + str(lw_id), 1)
                self._field_list = line.replace(' ', '')

                self.handle_header = False

            else:
                raise IOError('Error while parsing file ' + self._filename + '.')
        else:
            raise IOError('"Xdat:" not found in file ' + self._filename + '.')

        metadata['skip_rows'] = self._line_index

        return metadata

    def _extract_group_list(self):
        full_field_list = self._extract_field_list()
        group_list = []
        for field in full_field_list:
            # Add groups for MOBY attributes/fields
            groups = get_groups_for_product(field[0:2])
            if len(groups) == 0:
                continue

            for group in groups:
                if group not in group_list:
                    group_list.append(group)

        return group_list

    def _extract_field_list(self):
        if self._field_list is None:
            raise MobyFormatError('Missing header tag "fields"')
        return self._field_list.lower().split(',')

    def _extract_searchfields(self, dataset, metadata):
        self._extract_geo_locations(dataset)
        self._extract_times(dataset)

    def _extract_times(self, dataset):

        # Todo: Calculate mean lat and lon
        if 'lw_values' in self.metadata.keys() and 'es_values' in self.metadata.keys():

            dates = []

            lw_value_lists = self.metadata['lw_values']
            for lw_values in lw_value_lists:
                year = lw_values[0]
                month = lw_values[1]
                day = lw_values[2]
                hour = lw_values[3]
                minute = lw_values[4]
                sec = lw_values[5]
                date = str(year) + '-' + str(month).zfill(2) + '-'
                date += str(day).zfill(2) + ' ' + str(hour).zfill(2) + ':'
                date += str(minute).zfill(2) + ':' + str(sec).zfill(2)
                dates.append(date)

            es_value_lists = self.metadata['es_values']
            for es_values in es_value_lists:
                year = es_values[0]
                month = es_values[1]
                day = es_values[2]
                hour = es_values[3]
                minute = es_values[4]
                sec = es_values[5]
                date = str(year) + '-' + str(month).zfill(2) + '-'
                date += str(day).zfill(2) + ' ' + str(hour).zfill(2) + ':'
                date += str(minute).zfill(2) + ':' + str(sec).zfill(2)
                dates.append(date)

            date_arr = np.array(dates, dtype='datetime64[s]')
            date_mean = (date_arr.view('i8').mean().astype('datetime64[s]'))
        else:
            raise MobyFormatError('Lw values not found in metadata. ' +
                                  'Acquisition time not properly encoded')

        # Convert datetime64 to datetime
        ts = (date_mean - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        dt = datetime.datetime.utcfromtimestamp(ts)
        dataset.add_time(dt)

    def _extract_geo_locations(self, dataset):
        
        lats = []
        lons = []
        lon = None
        lat = None

        if 'lw_values' in self.metadata.keys():
            lw_value_lists = self.metadata['lw_values']

            for lw_values in lw_value_lists:
                lat = lw_values[6]
                lon = lw_values[7]
                lats.append(float(lat))
                lons.append(float(lon))
        else:
            raise MobyFormatError('Lw values not found in metadata.')
                    
        if 'es_values' in self.metadata.keys():
            es_value_lists = self.metadata['es_values']
            for es_values in es_value_lists:
                lat = es_values[6]
                lon = es_values[7]
                lats.append(float(lat))
                lons.append(float(lon))
        else:
            raise MobyFormatError('Es values not found in metadata.')

        dataset.add_geo_location(statistics.mean(lons), statistics.mean(lats))

        return True

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

    @classmethod
    def _extract_delimiter_regex(cls, metadata):
        if 'delimiter' not in metadata:
            raise MobyFormatError('Missing delimiter tag in header')

        delimiter = metadata['delimiter']
        if delimiter == 'comma':
            return ',+'
        elif delimiter == 'space':
            return '\s+'
        elif delimiter == 'tab':
            return '\t+'
        else:
            raise MobyFormatError('Invalid delimiter-value in header')

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
                raise MobyFormatError('No time zone given. ' +
                                      'Required all times be expressed as [GMT]')

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


# noinspection PyArgumentList
class MobyFormatError(Exception):
    """
    This error is raised if SbFileReader encounters format errors.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
