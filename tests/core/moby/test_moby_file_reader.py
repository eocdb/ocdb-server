# import datetime
import unittest

from ocdb.core.moby.moby_file_reader import  MobyFileReader, MobyFormatError
# from tests.helpers import new_test_db_dataset


class MobyFileReaderTest(unittest.TestCase):

    def test_read(self, fn, debug=False):
        reader = MobyFileReader()
        data_record = reader.read(fn)
        if debug:
            print(data_record)

    def setUp(self):
        self.reader = MobyFileReader()

    # moby_file = ['File: 1997072021D.MB\n',
    # '  File: 1997072021D.MBY\n',
    # '54 Variables, 629 Data Points\n',
    # '\n',
    # 'FhdS 1: MOBY203 Water-Leaving Radiance File\n',
    # 'FhdS 2: For Lw(s) 1  2  7\n',
    # 'FhdS 3:\n',
    # '\n',
    # '          META DATA:\n',
    # '              Year  Mon  Day Hour  Min  Sec       Lat       Lon   X-tilt   Y-tilt  Arm dir\n',
    # '                                            (DD.MMmm) (DD.MMmm)    (deg)    (deg) (deg True) \n',
    # 'LW1:          1997    7   20   21   49   39   20.4840 -157.1140    -0.46    -0.82   176.03 \n',
    # 'LW2:          1997    7   20   21   49   39   20.4840 -157.1140    -0.46    -0.82   176.03 \n',
    # 'LW7:          1997    7   20   22    0   56   20.4840 -157.1140    -0.77    -1.07   173.59 \n',
    # 'ES for LW1:   1997    7   20   21   49   54   20.4840 -157.1140    -0.80    -1.29   178.46 \n',
    # 'ES for LW2:   1997    7   20   21   49   54   20.4840 -157.1140    -0.80    -1.29   178.46 \n',
    # 'ES for LW7:   1997    7   20   22    1   12   20.4840 -157.1140    -1.21    -1.23   174.66\n',
    # '##Nov 2017 reprocessing applied on 07-Jan-2019 11:56:26 -------------------------------------------\n',
    # '## new matrix stray light correction applied\n',
    # '\n',
    # 'DscS  1: MOS Calibrated Wavelength (nm)\n',
    # 'DscS  2: Water-Leaving Radiance Lw1, Lu1 and Kl1(Lu1-Lu2) (µW/cm²/sr/nm)\n',
    # 'DscS  3: Water-Leaving Radiance Lw2, Lu1 and Kl2(Lu1-Lu3) (µW/cm²/sr/nm)\n\n'

    def test_parse_file_prefix_missing(self):
        moby_file = [ 'Fil: 1997072021D.MBY\n'
        ]
        with self.assertRaises(MobyFormatError) as cm:
            self.reader._parse(moby_file)
        expected_msg = 'First line does not correspond to pattern "File: [Filename]"'
        self.assertEqual(expected_msg, f"{cm.exception}")

    def test_parse_file_name_missing(self):
        moby_file = [ 'File: 1997072021D.MB\n'
        ]
        with self.assertRaises(MobyFormatError) as cm:
            self.reader._parse(moby_file)
        self.assertEqual('First line does not contain filename', f"{cm.exception.args[0][0:36]}")

    def test_parse_variables_data_points_missing_end(self):

        moby_file = ['File: 1997072021D.MBY\n',
                     'Variables, 629 Data Points']

        with self.assertRaises(MobyFormatError) as cm:
            self.reader._parse(moby_file)
        self.assertEqual('Check variables and points line', f"{cm.exception}")

    def test_comments_missing(self, comment_prefix):
        moby_file = ''
        if comment_prefix == 'FhdS':
            moby_file = ['File: 1997072021D.MBY\n',
                         '594 Variables, 629 Data Points\n',
                         'Fhd',   # S is Missing
                         '          META DATA:\n',
                         ''
                         ]
        elif comment_prefix == '##':
            moby_file = ['File: 1997072021D.MBY\n',
                         '594 Variables, 629 Data Points\n',
                         'FhdS',  # S is Missing
                         '          META DATA:\n',
                         '          Year  Mon  Day Hour  Min  Sec       Lat       Lon   X-tilt   Y-tilt  Arm dir\n',  # r in Year missing
                         '                                             (DD.MMmm)  (DD.MMmm)  (deg)  (deg)  (deg True)\n',
                         '\n',
                         '\n',
                         '  LW1:          1997    7   20   21   49   39   20.4840 -157.1140    -0.46    -0.82   176.03 ',
                         '  ES for LW1:   1997    7   20   21   49   54   20.4840 -157.1140    -0.80    -1.29   178.46 ',
                         '']

        elif comment_prefix == 'DscS':
            moby_file = ['File: 1997072021D.MBY\n',
                         '594 Variables, 629 Data Points\n',
                         'FhdS',  # S is Missing
                         '          META DATA:\n',
                         '          Year  Mon  Day Hour  Min  Sec       Lat       Lon   X-tilt   Y-tilt  Arm dir\n',  # r in Year missing
                         '                                             (DD.MMmm)  (DD.MMmm)  (deg)  (deg)  (deg True)\n',
                         '\n',
                         '\n',
                         '  LW1:          1997    7   20   21   49   39   20.4840 -157.1140    -0.46    -0.82   176.03 ',
                         '  ES for LW1:   1997    7   20   21   49   54   20.4840 -157.1140    -0.80    -1.29   178.46 ',
                         '  ##hkjghjgghgh']

        with self.assertRaises(MobyFormatError) as cm:
            self.reader._parse(moby_file)
        self.assertEqual(comment_prefix + ' comments missing.', f"{cm.exception}")

    def test_metadata_tag_missing(self):
        moby_file = ['File: 1997072021D.MBY\n',
                     '594 Variables, 629 Data Points\n',
                     'FhdS',   # S is Missing
                     '          META DAT:\n',
                     ''
                     ]
        with self.assertRaises(MobyFormatError) as cm:
            self.reader._parse(moby_file)
        self.assertEqual('Metadata tag missing.', f"{cm.exception}")

    def test_date_and_time_columns_missing(self):
        moby_file = ['File: 1997072021D.MBY\n',
                     '594 Variables, 629 Data Points\n',
                     'FhdS',   # S is Missing
                     '          META DATA:\n',
                     '          Yea  Mon  Day Hour  Min  Sec       Lat       Lon   X-tilt   Y-tilt  Arm dir'    # r in Year missing
                     ]
        with self.assertRaises(MobyFormatError) as cm:
            self.reader._parse(moby_file)
        expected_msg = 'Date and time columns missing in metadata columns, ' + \
                       'i. e. Year, Mon, Day, Hour, Min, Sec, ... .'
        self.assertEqual(expected_msg, f"{cm.exception}")

    def test_date_and_time_units_missing(self):
        moby_file = ['File: 1997072021D.MBY\n',
                     '594 Variables, 629 Data Points\n',
                     'FhdS',   # S is Missing
                     '          META DATA:\n',
                     '          Year  Mon  Day Hour  Min  Sec       Lat       Lon   X-tilt   Y-tilt  Arm dir\n',    # r in Year missing
                     '                                             (DD.MMmm)  (DD.MMmm)  (deg)  (deg) \n',
                     '\n'
        ]
        with self.assertRaises(MobyFormatError) as cm:
            self.reader._parse(moby_file)
        expected_msg = 'Wrong number of metadata column units.'
        self.assertEqual(expected_msg, f"{cm.exception}")

    def test_lw_metadata_missing(self):
        moby_file = ['File: 1997072021D.MBY\n',
                     '594 Variables, 629 Data Points\n',
                     'FhdS',   # S is Missing
                     '          META DATA:\n',
                     '          Year  Mon  Day Hour  Min  Sec       Lat       Lon   X-tilt   Y-tilt  Arm dir\n',    # r in Year missing
                     '                                             (DD.MMmm)  (DD.MMmm)  (deg)  (deg)  (deg True)\n',
                     '\n',
                     '\n',
                     '  L1:          1997    7   20   21   49   39   20.4840 -157.1140    -0.46    -0.82   176.03 '
        ]
        with self.assertRaises(MobyFormatError) as cm:
            self.reader._parse(moby_file)
        expected_msg = 'Lw metadata missing.'
        self.assertEqual(expected_msg, f"{cm.exception}")

    def test_es_metadata_missing(self):
        moby_file = ['File: 1997072021D.MBY\n',
                     '594 Variables, 629 Data Points\n',
                     'FhdS',   # S is Missing
                     '          META DATA:\n',
                     '          Year  Mon  Day Hour  Min  Sec       Lat       Lon   X-tilt   Y-tilt  Arm dir\n',    # r in Year missing
                     '                                             (DD.MMmm)  (DD.MMmm)  (deg)  (deg)  (deg True)\n',
                     '\n',
                     '\n',
                     '  LW1:          1997    7   20   21   49   39   20.4840 -157.1140    -0.46    -0.82   176.03 ',
                     ''
        ]
        with self.assertRaises(MobyFormatError) as cm:
            self.reader._parse(moby_file)
        expected_msg = 'Es metadata missing.'
        self.assertEqual(expected_msg, f"{cm.exception}")

    def test_xdata_header_missing(self):
        moby_file = ['File: 1997072021D.MBY\n',
                         '594 Variables, 629 Data Points\n',
                         'FhdS',  # S is Missing
                         '          META DATA:\n',
                         '          Year  Mon  Day Hour  Min  Sec       Lat       Lon   X-tilt   Y-tilt  Arm dir\n',  # r in Year missing
                         '                                             (DD.MMmm)  (DD.MMmm)  (deg)  (deg)  (deg True)\n',
                         '\n',
                         '\n',
                         '  LW1:          1997    7   20   21   49   39   20.4840 -157.1140    -0.46    -0.82   176.03 \n',
                         '  ES for LW1:   1997    7   20   21   49   54   20.4840 -157.1140    -0.80    -1.29   178.46 \n',
                         '  ##hkjghjgghgh\n',
                         '  DscS  1: MOS Calibrated Wavelength (nm)  \n']
        with self.assertRaises(MobyFormatError) as cm:
            self.reader._parse(moby_file)
        expected_msg = '"Xdat:" not found.'
        self.assertEqual(expected_msg, f"{cm.exception}")

    def test_wrong_number_of_values(self, debug=False):

        moby_path = 'L:/ongoing/FRM4SOC/data/MOBY/Downloads/203/'
        moby_fn = 'M203_1997072021D.txt'

        moby_file = ['File: ' + moby_fn[5:].replace('txt', 'MBY') + '\n',
                         '594 Variables, 629 Data Points\n',
                         'FhdS',  # S is Missing
                         '          META DATA:\n',
                         '          Year  Mon  Day Hour  Min  Sec       Lat       Lon   X-tilt   Y-tilt  Arm dir\n',  # r in Year missing
                         '                                             (DD.MMmm)  (DD.MMmm)  (deg)  (deg)  (deg True)\n',
                         '\n',
                         '\n',
                         '  LW1:          1997    7   20   21   49   39   20.4840 -157.1140    -0.46    -0.82   176.03 \n',
                         '  ES for LW1:   1997    7   20   21   49   54   20.4840 -157.1140    -0.80    -1.29   178.46 \n',
                         '  ##hkjghjgghgh\n',
                         '  DscS  1: MOS Calibrated Wavelength (nm)  \n',
                     'Xdat:\n',
                     '   lambda,         Lw1,         Lw2,         Lw7,  Ed Sfc,  Ed Sfc,  Ed Sfc,        Lw21,        Lw27,        Lw22\n',
                     '348.4221, 0.988740, 0.977193, 0.908520,,,, 0.988740, 0.908520, 0.977193\n',
                     '348.9953, 0.975660, 0.965026, 0.905604,,, 0.975660, 0.905604, 0.965026'
        ]
        with self.assertRaises(MobyFormatError) as cm:
            self.reader._filename = moby_path + moby_fn
            self.reader._parse(moby_file, debug=debug)
        expected_msg = 'Wrong number of values.'
        self.assertEqual(expected_msg, f"{cm.exception}")
