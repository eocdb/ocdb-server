import unittest

from eocdb.core.seabass.sb_file_reader import SbFileReader


class SbFileReaderTest(unittest.TestCase):

    # def test_read(self):
    #     reader = SbFileReader()
    #     data_record = reader.read("/usr/local/data/OC_DB/bio_1535713657890739/AWI/PANGAEA/SO218/archive/SO218_pigments.sb")
    #     print(data_record)

    def test_parse_empty_header_no_records(self):
        sb_file = ['/begin_header\n',
                   '/end_header\n']

        reader = SbFileReader()
        document = reader._parse(sb_file)

