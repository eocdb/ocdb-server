import unittest

from eocdb.core.seabass.sb_file_reader import SbFileReader
from eocdb.db.db_dataset import DbDataset


class SbFileReaderTest(unittest.TestCase):

    # def test_read(self):
    #     reader = SbFileReader()
    #     data_record = reader.read("/usr/local/data/OC_DB/bio_1535713657890739/AWI/PANGAEA/SO218/archive/SO218_pigments.sb")
    #     print(data_record)

    def setUp(self):
        self.reader = SbFileReader()

    def test_parse_empty_header_missing_begin(self):
        sb_file = ['/end_header\n']

        try:
            self.reader._parse(sb_file)
            self.fail("IOError expected")
        except IOError:
            pass

    def test_parse_empty_header_missing_end(self):
        sb_file = ['/begin_header\n']

        try:
            self.reader._parse(sb_file)
            self.fail("IOError expected")
        except IOError:
            pass

    def test_parse_location_in_header(self):
        sb_file = ['/begin_header\n',
                   '/data_file_name=pro_03_04AA_L2s.dat\n',
                   '/data_type=cast\n',
                   '/data_status=preliminary\n',
                   '/experiment=LAMONT_SCS\n',
                   '!/experiment=JUN16SCS\n',
                   '/cruise=jun16scs\n',
                   '!/cruise=FK160603\n',
                   '/station=03_04\n',
                   '/delimiter=comma\n',
                   '/end_header\n']

        document = self.reader._parse(sb_file)
        self.assertEqual({'data_file_name': 'pro_03_04AA_L2s.dat', 'data_type': 'cast', 'data_status': 'preliminary', 'experiment': 'LAMONT_SCS', 'cruise': 'jun16scs', 'station': '03_04', 'delimiter': 'comma'}, document.metadata)
        self.assertEqual(0, document.attribute_count)
        self.assertEqual(0, document.record_count)

    def test_extract_delimiter_regex(self):
        dataset = DbDataset()
        dataset.set_metadata({'delimiter': 'comma'})

        regex = self.reader._extract_delimiter_regex(dataset)
        self.assertEqual(",+", regex)

        dataset.set_metadata({'delimiter': 'space'})
        regex = self.reader._extract_delimiter_regex(dataset)
        self.assertEqual("\s+", regex)

        dataset.set_metadata({'delimiter': 'tab'})
        regex = self.reader._extract_delimiter_regex(dataset)
        self.assertEqual("\t+", regex)

    def test_extract_delimiter_regex_invalid(self):
        dataset = DbDataset()
        dataset.set_metadata({'delimiter': 'double-slash-and-semicolon'})

        try:
            self.reader._extract_delimiter_regex(dataset)
            self.fail("IOException expected")
        except IOError:
            pass

    def test_extract_delimiter_regex_missing(self):
        dataset = DbDataset()

        try:
            self.reader._extract_delimiter_regex(dataset)
            self.fail("IOException expected")
        except IOError:
            pass