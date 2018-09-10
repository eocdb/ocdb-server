import re

from eocdb.db.db_dataset import DbDataset

EOF = 'end_of_file'

class SbFileReader():

    def __init__(self):
        self.lines = []
        self.line_index = 0

    def read(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            return self._parse(lines)

    def _parse(self, lines):
        dataset = DbDataset()
        self.lines = lines

        self.handle_header = None

        line = self._next_line()
        if '/begin_header' in line.lower():
            self.handle_header = True
            self._parse_header(dataset)

        self._interprete_header(dataset)
        self._parse_records(dataset)
        self._extract_searchfields(dataset)

        if self.handle_header is None or self.handle_header is True:
            raise IOError("/end_header tag missing")

        return dataset

    def _next_line(self) -> str:
        if self.line_index < len(self.lines):
            line = self.lines[self.line_index]
            self.line_index += 1
            return line

        return EOF

    def _parse_header(self, dataset):
        while True:
            line = self._next_line()
            if line == EOF:
                break

            # strip comments
            if line.startswith('!'):
                continue

            # done with header
            if '/end_header' in line.lower():
                if self.handle_header == True:
                    self.handle_header = False
                    break
                else:
                    raise IOError("/end_header tag found without /begin_header")

            # split line, trim and remove leading slash
            line = re.sub("[\r\n]+", '', line).strip()
            [key, value] = line.split('=', 1)
            key = key[1:].strip()
            value = value.strip()
            if key == 'fields':
                self.field_list = value
            else:
                dataset.add_metadatum(key, value)

    def _interprete_header(self, dataset):
        self._delimiter_regex = self._extract_delimiter_regex(dataset)

        if self.field_list is None:
            raise IOError('Missing header tag "fields"')

        variable_names = self.field_list.lower().split(',')
        dataset.add_attributes(variable_names)

    def _extract_searchfields(self, dataset):

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
            raise IOError("geolocation not properly encoded")

    # @todo 1 tb/tb write test 2018-09-12
    def _extract_geo_location_form_header(self, dataset):
        east_lon_string = dataset.metadata['east_longitude']
        lon = self._extract_angle(east_lon_string)
        north_lat_string = dataset.metadata['north_latitude']
        lat = self._extract_angle(north_lat_string)
        dataset.add_geo_location(lon, lat)

    def _parse_records(self, dataset):
        while True:
            line = self._next_line()
            if line == EOF:
                break

            tokens = re.split(self._delimiter_regex, line)
            record = []
            for token in tokens:
                if self._is_number(token):
                    if self._is_integer(token):
                        record.append(int(token))
                    else:
                        record.append(float(token))
                else:
                    record.append(token)

            dataset.add_record(record)

    def _extract_delimiter_regex(self, dataset):
        if not 'delimiter' in dataset.metadata:
            raise IOError('Missing delimiter tag in header')

        delimiter = dataset.metadata['delimiter']
        if delimiter == 'comma':
            return ',+'
        elif delimiter == 'space':
            return '\s+'
        elif delimiter == 'tab':
            return '\t+'
        else:
            raise IOError('Invalid delimiter-value in header')

    def _is_number(self, token):
        try:
            float(token)
            return True
        except ValueError:
            return False

    def _is_integer(self, token):
        try:
            int(token)
            return True
        except ValueError:
            return False

    def _extract_angle(self, angle_str):
        parse_str = angle_str
        if '[' in angle_str:
            unit_index = parse_str.find('[')
            parse_str= angle_str[0:unit_index]
        return float(parse_str)
