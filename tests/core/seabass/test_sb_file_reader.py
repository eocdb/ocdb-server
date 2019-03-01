import datetime
import unittest

from eocdb.core.seabass.sb_file_reader import SbFileReader, SbFormatError
from tests.helpers import new_test_db_dataset


class SbFileReaderTest(unittest.TestCase):

    # def test_read(self):
    #     reader = SbFileReader()
    #     data_record = reader.read("/fs1/temp/Tom/test2.txt")
    #     print(data_record)

    def setUp(self):
        self.reader = SbFileReader()

    def test_parse_empty_header_missing_begin(self):
        sb_file = ['/end_header\n']
        with self.assertRaises(SbFormatError) as cm:
            self.reader._parse(sb_file)
        self.assertEqual('Missing delimiter tag in header', f"{cm.exception}")

    def test_parse_empty_header_missing_end(self):
        sb_file = ['/begin_header\n']
        with self.assertRaises(SbFormatError) as cm:
            self.reader._parse(sb_file)
        self.assertEqual('Missing delimiter tag in header', f"{cm.exception}")

    def test_parse_location_in_header_time_info_in_header_and_records(self):
        sb_file = ['/begin_header\n',
                   '/data_file_name=pro_03_04AA_L2s.dat\n',
                   '/data_type=cast\n',
                   '/data_status=preliminary\n',
                   '/affiliations = IMARPE\n',
                   '/experiment=LAMONT_SCS\n',
                   '!/experiment=JUN16SCS\n',
                   '/cruise=jun16scs\n',
                   '!/cruise=FK160603\n',
                   '/station=03_04\n',
                   '/start_date=20020616\n',
                   '/north_latitude=11.713[DEG]\n',
                   '/south_latitude=11.713[DEG]\n',
                   '/west_longitude=109.587[DEG]\n',
                   '/east_longitude=109.587[DEG]\n',
                   '/delimiter=comma\n',
                   '/fields=time,depth,ED379.9,ED412.1,ED442.6,ED470.4,ED490.5,ED510.8,ED532.4,ED555.3,ED589.6,ED619.7,ED669.8,ED683.3,ED704.9,ED779.4,LU380.3,LU470.4,LU510.1,LU589.8,LU619.7,LU704.8,LU779.9,tilt,COND,Wt,pvel\n',
                   '/end_header\n',
                   '05:42:49,0.40000000,56.61060942,122.66957337,132.33737132,114.44906813,121.14584599,129.14107229,164.93812382,153.82678513,107.74022908,74.84475416,112.73332494,117.61951804,44.97546967,12.29104733,-999,-999,-999,-999,-999,-999,-999,-999,-999,-999,-999',
                   '05:42:50,0.50000000,56.90948085,115.97783666,171.51381329,100.38906060,161.96556721,113.75394300,113.36437951,77.19171621,94.68081637,74.03389812,80.24165958,92.87650441,41.91937544,7.05047058,-999,-999,-999,-999,-999,-999,-999,2.32841663,53.06609583,27.46488778,0.37780480']

        dataset = self.reader._parse(sb_file)
        self.assertEqual({'affiliations': 'IMARPE', 'data_file_name': 'pro_03_04AA_L2s.dat', 'data_type': 'cast',
                          'data_status': 'preliminary',
                          'experiment': 'LAMONT_SCS',
                          'fields': 'time,depth,ED379.9,ED412.1,ED442.6,ED470.4,ED490.5,ED510.8,ED532.4,ED555.3,ED589.6,ED619.7,ED669.8,ED683.3,ED704.9,ED779.4,LU380.3,LU470.4,LU510.1,LU589.8,LU619.7,LU704.8,LU779.9,tilt,COND,Wt,pvel',
                          'cruise': 'jun16scs', 'station': '03_04', 'delimiter': 'comma',
                          'east_longitude': '109.587[DEG]', 'west_longitude': '109.587[DEG]',
                          'north_latitude': '11.713[DEG]', 'south_latitude': '11.713[DEG]', 'start_date': '20020616'},
                         dataset.metadata)

        self.assertEqual(27, dataset.attribute_count)
        self.assertEqual("time", dataset.attribute_names[0])
        self.assertEqual("lu470.4", dataset.attribute_names[17])

        self.assertEqual(2, dataset.record_count)
        self.assertEqual('05:42:50', dataset.records[1][0])
        self.assertAlmostEqual(56.90948085, dataset.records[1][2])
        self.assertEqual(-999, dataset.records[1][21])
        self.assertEqual(27, len(dataset.records[0]))

        self.assertEqual(1, len(dataset.longitudes))
        self.assertEqual(1, len(dataset.latitudes))
        self.assertAlmostEqual(109.587, dataset.longitudes[0], 8)
        self.assertAlmostEqual(11.713, dataset.latitudes[0], 8)

    def test_parse_location_in_records_time_info_in_separate_record_fields(self):
        sb_file = ['/begin_header\n',
                   '/delimiter=space\n',
                   '/fields=year,month,day,hour,minute,second,lat,lon,CHL,depth\n',
                   '/end_header\n',
                   '1992 03 01 23 04 00 12.00 -110.03 0.1700 18\n',
                   '1992 03 01 23 04 00 12.00 -110.03 0.1900 29\n',
                   '1992 03 01 23 04 00 12.00 -110.03 0.4600 46\n',
                   '1992 03 01 23 04 00 12.00 -110.03 0.3600 70\n']

        dataset = self.reader._parse(sb_file)
        self.assertEqual({'delimiter': 'space', 'fields': 'year,month,day,hour,minute,second,lat,lon,CHL,depth'},
                         dataset.metadata)

        self.assertEqual(10, dataset.attribute_count)
        self.assertEqual("month", dataset.attribute_names[1])
        self.assertEqual("second", dataset.attribute_names[5])

        self.assertEqual(4, dataset.record_count)
        self.assertEqual(3, dataset.records[2][1])
        self.assertEqual(23, dataset.records[2][3])
        self.assertAlmostEqual(-110.03, dataset.records[2][7], 8)
        self.assertEqual(10, len(dataset.records[0]))

        self.assertEqual(4, len(dataset.longitudes))
        self.assertEqual(4, len(dataset.latitudes))
        self.assertAlmostEqual(-110.03, dataset.longitudes[1], 8)
        self.assertAlmostEqual(12.0, dataset.latitudes[1], 8)

        self.assertEqual(4, len(dataset.times))
        self.assertEqual(datetime.datetime(1992, 3, 1, 23, 4, 0), dataset.times[3])

    def test_parse_location_in_records_time_info_in_separate_record_fields_missing_seconds(self):
        sb_file = ['/begin_header\n',
                   '/delimiter=space\n',
                   '/fields=year,month,day,hour,minute,lat,lon,CHL,depth\n',
                   '/end_header\n',
                   '1992 03 01 23 04 12.00 -110.03 0.1700 18\n',
                   '1992 03 01 23 04 12.00 -110.03 0.1900 29\n',
                   '1992 03 01 23 04 12.00 -110.03 0.4600 46\n',
                   '1992 03 01 23 04 12.00 -110.03 0.3600 70\n']

        dataset = self.reader._parse(sb_file)
        self.assertEqual({'delimiter': 'space', 'fields': 'year,month,day,hour,minute,lat,lon,CHL,depth'},
                         dataset.metadata)

        self.assertEqual(9, dataset.attribute_count)
        self.assertEqual("month", dataset.attribute_names[1])
        self.assertEqual("lon", dataset.attribute_names[6])

        self.assertEqual(4, dataset.record_count)
        self.assertEqual(3, dataset.records[2][1])
        self.assertEqual(23, dataset.records[2][3])
        self.assertAlmostEqual(0.46, dataset.records[2][7], 8)
        self.assertEqual(9, len(dataset.records[0]))

        self.assertEqual(4, len(dataset.latitudes))
        self.assertEqual(4, len(dataset.longitudes))
        self.assertAlmostEqual(-110.03, dataset.longitudes[1], 8)
        self.assertAlmostEqual(12.0, dataset.latitudes[1], 8)

        self.assertEqual(4, len(dataset.times))
        self.assertEqual(datetime.datetime(1992, 3, 1, 23, 4, 0), dataset.times[3])

    def test_parse_time_in_header(self):
        sb_file = ['/begin_header\n',
                   '/delimiter=space\n',
                   '/north_latitude=26.957[DEG]\n',
                   '/east_longitude=125.198[DEG]\n',
                   '/start_date=20010723\n',
                   '/end_date=20010723\n',
                   '/start_time=00:08:00[GMT]\n',
                   '/end_time=00:08:00[GMT]\n',
                   '/fields=depth,CHL\n',
                   '/end_header\n',
                   '2.000000 0.158000\n',
                   '3.000000 0.158000\n',
                   '4.000000 0.158000\n',
                   '5.000000 0.158000\n',
                   '6.000000 0.158000\n']

        dataset = self.reader._parse(sb_file)
        self.assertEqual({'delimiter': 'space', 'east_longitude': '125.198[DEG]', 'end_date': '20010723',
                          'end_time': '00:08:00[GMT]', 'fields': 'depth,CHL',
                          'north_latitude': '26.957[DEG]', 'start_date': '20010723',
                          'start_time': '00:08:00[GMT]'}, dataset.metadata)

        self.assertEqual(1, len(dataset.times))
        self.assertEqual(datetime.datetime(2001, 7, 23, 0, 8, 0), dataset.times[0])

    def test_parse_time_in_records_date_time(self):
        sb_file = ['/begin_header\n',
                   '/delimiter=space\n',
                   '/north_latitude=22.442[DEG]\n',
                   '/east_longitude=114.196[DEG]\n',
                   '/start_date=20010510\n',
                   '/end_date=20010510\n',
                   '/start_time=04:37:00[GMT]\n',
                   '/end_time=04:37:00[GMT]\n',
                   '/fields=date,time,depth,ad,wavelength\n',
                   '/end_header\n',
                   '20010510 04:37:00 0.0 1.0340 300\n',
                   '20010510 04:37:00 0.0 1.0340 301\n',
                   '20010510 04:37:00 0.0 1.0330 302\n',
                   '20010510 04:37:00 0.0 1.0310 303\n',
                   '20010510 04:37:00 0.0 1.0290 304\n']

        dataset = self.reader._parse(sb_file)
        self.assertEqual({'delimiter': 'space', 'east_longitude': '114.196[DEG]', 'end_date': '20010510',
                          'end_time': '04:37:00[GMT]', 'fields': 'date,time,depth,ad,wavelength',
                          'north_latitude': '22.442[DEG]', 'start_date': '20010510',
                          'start_time': '04:37:00[GMT]'}, dataset.metadata)

        self.assertEqual(5, len(dataset.times))
        self.assertEqual(datetime.datetime(2001, 5, 10, 4, 37, 0), dataset.times[2])

    def test_parse_attributes(self):
        sb_file = ['/begin_header\n',
                   '/delimiter=tab\n',
                   '/north_latitude=78.77067[DEG]\n',
                   '/east_longitude=-104.72140[DEG\n',
                   '/start_date=20110411\n',
                   '/end_date=220110411\n',
                   '/start_time=14:48:00[GMT]\n',
                   '/end_time=17:48:00[GMT]\n',
                   '/fields=depth,Wt,sal,agp412,agp440,agp488,agp510,agp532,agp555,agp650,agp676,agp715,cgp412,cgp440,cgp488,cgp510,cgp532,cgp555,cgp650,cgp676,cgp715\n',
                   '/end_header\n',
                   '1.0	-1.67 	 30.515 	 0.172957 	 0.114344 	 0.064189 	 0.053668 	 0.046506 	 0.041751 	 0.03159 	 0.030531 	 0.025931 	 0.246614 	 0.178616 	 0.134436 	 0.1365 	 0.104338 	 0.098068 	 0.080178 	 0.080863 	 0.071719\n',
                   '1.5	-1.671 	 30.514 	 0.157698 	 0.098079 	 0.051644 	 0.042618 	 0.035022 	 0.030336 	 0.020861 	 0.019751 	 0.016011 	 0.227774 	 0.155066 	 0.104526 	 0.08393 	 0.084763 	 0.071008 	 0.056643 	 0.045593 	 0.041029\n',
                   '2.0	-1.671 	 30.486 	 0.138603 	 0.081831 	 0.033446 	 0.024684 	 0.018127 	 0.013611 	 0.003874 	 0.003721 	 0.001485 	 0.206371 	 0.137294 	 0.085409 	 0.074618 	 0.065446 	 0.058116 	 0.036772 	 0.035281 	 0.028068\n',
                   '2.5	-1.671 	 30.489 	 0.138417 	 0.081566 	 0.032896 	 0.02452 	 0.017878 	 0.013523 	 0.003648 	 0.003748 	 0.001215 	 0.192826 	 0.123139 	 0.071535 	 0.058058 	 0.047781 	 0.040366 	 0.020996 	 0.016802 	 0.014773\n',
                   '3.0	-1.672 	 30.473 	 0.140683 	 0.084343 	 0.035572 	 0.027182 	 0.020158 	 0.01573 	 0.005666 	 0.005809 	 0.002923 	 0.194957 	 0.124843 	 0.073786 	 0.059254 	 0.049095 	 0.041698 	 0.022461 	 0.018807 	 0.016752\n']

        dataset = self.reader._parse(sb_file)
        self.assertEqual(2, len(dataset.groups))
        self.assertEqual("CTD", dataset.groups[0])
        self.assertEqual("a", dataset.groups[1])

        self.assertEqual(21, len(dataset.attributes))
        self.assertEqual("depth", dataset.attributes[0])
        self.assertEqual("sal", dataset.attributes[2])
        self.assertEqual("agp412", dataset.attributes[3])
        self.assertEqual("agp440", dataset.attributes[4])
        self.assertEqual("cgp488", dataset.attributes[14])

    def test_extract_delimiter_regex(self):
        metadata = {'delimiter': 'comma'}

        regex = self.reader._extract_delimiter_regex(metadata)
        self.assertEqual(",+", regex)

        metadata = {'delimiter': 'space'}
        regex = self.reader._extract_delimiter_regex(metadata)
        self.assertEqual("\s+", regex)

        metadata = {'delimiter': 'tab'}
        regex = self.reader._extract_delimiter_regex(metadata)
        self.assertEqual("\t+", regex)

    def test_extract_delimiter_regex_invalid(self):
        metadata = {'delimiter': 'double-slash-and-semicolon'}
        with self.assertRaises(SbFormatError) as cm:
            self.reader._extract_delimiter_regex(metadata)
        self.assertEqual("Invalid delimiter-value in header", f"{cm.exception}")

    def test_extract_delimiter_regex_missing(self):
        metadata = {}
        with self.assertRaises(SbFormatError) as cm:
            self.reader._extract_delimiter_regex(metadata)
        self.assertEqual("Missing delimiter tag in header", f"{cm.exception}")

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

    def test_extract_angle_value(self):
        self.assertAlmostEqual(1.7654, self.reader._extract_angle("1.7654[DEG]"), 8)
        self.assertAlmostEqual(-76.33454, self.reader._extract_angle("-76.33454[DEG]"), 8)
        self.assertAlmostEqual(0.5521, self.reader._extract_angle("0.5521"), 8)
        self.assertAlmostEqual(-2.00987, self.reader._extract_angle("-2.00987"), 8)

    def test_extract_date(self):
        self.assertEqual(datetime.datetime(2002, 7, 11, 14, 22, 53),
                         self.reader._extract_date("20020711", "14:22:53[GMT]"))

    def test_extract_date_no_leading_zero(self):
        self.assertEqual(datetime.datetime(2002, 7, 11, 2, 23, 54),
                         self.reader._extract_date("20020711", "2:23:54[GMT]"))

    def test_extract_date_throws_on_missing_GMT(self):
        with self.assertRaises(SbFormatError) as cm:
            datetime.datetime(2002, 7, 11, 14, 22, 53), self.reader._extract_date("20030812", "15:23:54",
                                                                                  check_gmt=True)
        self.assertEqual("No time zone given. Required all times be expressed as [GMT]", f"{cm.exception}")

        with self.assertRaises(SbFormatError) as cm:
            datetime.datetime(2002, 7, 11, 14, 22, 53), self.reader._extract_date("20030812", "15:23:54",
                                                                                  check_gmt=True)
        self.assertEqual("No time zone given. Required all times be expressed as [GMT]", f"{cm.exception}")

    def test_extract_date_missing_GMT_ignored_if_requested(self):
        datetime.datetime(2003, 8, 12, 15, 23, 54), self.reader._extract_date("20030812", "15:23:54", check_gmt=False)

    def test_extract_geo_location_from_header(self):
        dataset = new_test_db_dataset(2)
        dataset.add_metadatum('east_longitude', '22.7')
        dataset.add_metadatum('north_latitude', '-17.09')

        self.reader._extract_geo_location_from_header(dataset)

        self.assertEqual(1, len(dataset.longitudes))
        self.assertEqual(1, len(dataset.latitudes))
        self.assertAlmostEqual(22.7, dataset.longitudes[0], 8)
        self.assertAlmostEqual(-17.09, dataset.latitudes[0], 8)
