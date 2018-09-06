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
        self.assertEqual(0, document.attribute_count)
        self.assertEqual(0, document.record_count)
        self.assertEqual(dict(), document.metadata)

    def test_parse_empty_header_missing_begin(self):
        sb_file = ['/end_header\n']

        try:
            reader = SbFileReader()
            reader._parse(sb_file)
            self.fail("IOError expected")
        except IOError:
            pass

    def test_parse_empty_header_missing_end(self):
        sb_file = ['/begin_header\n']

        try:
            reader = SbFileReader()
            reader._parse(sb_file)
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

        reader = SbFileReader()
        document = reader._parse(sb_file)
        self.assertEqual({'data_file_name': 'pro_03_04AA_L2s.dat', 'data_type': 'cast', 'data_status': 'preliminary', 'experiment': 'LAMONT_SCS', 'cruise': 'jun16scs', 'station': '03_04', 'delimiter': 'comma'}, document.metadata)
        self.assertEqual(0, document.attribute_count)
        self.assertEqual(0, document.record_count)
