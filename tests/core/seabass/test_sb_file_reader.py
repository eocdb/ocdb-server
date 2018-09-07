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
                   '/fields=time,depth,ED379.9,ED412.1,ED442.6,ED470.4,ED490.5,ED510.8,ED532.4,ED555.3,ED589.6,ED619.7,ED669.8,ED683.3,ED704.9,ED779.4,LU380.3,LU470.4,LU510.1,LU589.8,LU619.7,LU704.8,LU779.9,tilt,COND,Wt,pvel\n',
                   '/end_header\n',
                   '05:42:49,0.40000000,56.61060942,122.66957337,132.33737132,114.44906813,121.14584599,129.14107229,164.93812382,153.82678513,107.74022908,74.84475416,112.73332494,117.61951804,44.97546967,12.29104733,-999,-999,-999,-999,-999,-999,-999,-999,-999,-999,-999',
                   '05:42:50,0.50000000,56.90948085,115.97783666,171.51381329,100.38906060,161.96556721,113.75394300,113.36437951,77.19171621,94.68081637,74.03389812,80.24165958,92.87650441,41.91937544,7.05047058,-999,-999,-999,-999,-999,-999,-999,2.32841663,53.06609583,27.46488778,0.37780480']

        document = self.reader._parse(sb_file)
        self.assertEqual({'data_file_name': 'pro_03_04AA_L2s.dat', 'data_type': 'cast', 'data_status': 'preliminary',
                          'experiment': 'LAMONT_SCS', 'cruise': 'jun16scs', 'station': '03_04', 'delimiter': 'comma'}, document.metadata)

        self.assertEqual(27, document.attribute_count)
        self.assertEqual("time", document.attribute_names[0])
        self.assertEqual("lu470.4", document.attribute_names[17])

        self.assertEqual(2, document.record_count)
        self.assertEqual('05:42:50', document.records[1][0])
        self.assertAlmostEqual(56.90948085, document.records[1][2])
        self.assertEqual(-999, document.records[1][21])
        self.assertEqual(27, len(document.records[0]))

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

    def test_is_number(self):
        self.assertTrue(self.reader._is_number('1246'))
        self.assertTrue(self.reader._is_number('0.2376'))
        self.assertFalse(self.reader._is_number('23:07:33'))
        self.assertFalse(self.reader._is_number('nasenmann'))

    def test_is_integer(self):
        self.assertTrue(self.reader._is_integer('1246'))
        self.assertTrue(self.reader._is_integer('-999'))
        self.assertFalse(self.reader._is_integer('0.25216'))
        self.assertFalse(self.reader._is_integer('23:07:33'))
        self.assertFalse(self.reader._is_integer('rattelschneck'))