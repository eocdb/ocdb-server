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

