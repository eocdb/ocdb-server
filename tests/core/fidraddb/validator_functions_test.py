import copy
import unittest
from unittest.mock import MagicMock
import ocdb.core.fidraddb.validator as v
from ocdb.core.fidraddb.validator import CalCharValidator


class ValidatorCreationTest(unittest.TestCase):

    def testThatLinesAreReadInSplittedAndStriped(self):
        # preparation
        file_mock = MagicMock()
        file_mock.readlines.return_value = [
            'abc;d ef ; ghi \n',
            ' 12; jk24;\n\t\r',
            'l;m; n;o   ;p'
        ]

        # execution
        actual = v.read_lines_split_and_strip(file_mock)

        # validation
        expected = [
            ['abc', 'd ef', 'ghi'],
            ['12', 'jk24', ''],
            ['l', 'm', 'n', 'o', 'p']
        ]
        self.assertEqual(expected, actual)

    def testThatTransposeThrowsTypeExceptionIfTheArgumentIsNotAListOfList(self):
        with self.assertRaises(TypeError) as te:
            v.transpose_list_per_row_to_list_per_column(None)
        self.assertEqual('list of lists expected', str(te.exception))

        with self.assertRaises(TypeError) as te:
            v.transpose_list_per_row_to_list_per_column("aaaa")
        self.assertEqual('list of lists expected', str(te.exception))

        with self.assertRaises(TypeError) as te:
            v.transpose_list_per_row_to_list_per_column(['aa', 'bb'])
        self.assertEqual('list of lists expected', str(te.exception))

        with self.assertRaises(TypeError) as te:
            v.transpose_list_per_row_to_list_per_column([('aa', 'bb')])
        self.assertEqual('list of lists expected', str(te.exception))

        # valid
        v.transpose_list_per_row_to_list_per_column([['aa', 'bb']])

    def testTranspositionFromRowsToColumns(self):
        # preparation
        rows = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]

        # execution
        columns = v.transpose_list_per_row_to_list_per_column(rows)

        # validation
        expected = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
        self.assertEqual(expected, columns)

    def testThatGapsInFileTypeFunctionColumnsAreFilled(self):
        # preparation
        column_names = ["any", "F_ab", "ANY", "Function", "Any", "F_cd"]
        cols = [
            [11, 12, 13, 14, 15],  # column any
            ["", "w", "", "v", ""],  # column F_ab
            [21, 22, 23, 24, 25],  # column ANY
            ["a", "b", "c", "d", "e"],  # column Function
            [31, 32, 33, 34, 35],  # column Any
            ["z", "", "y", "", "x"],  # column F_cd
        ]
        expected = copy.deepcopy(cols)

        # execution
        v.fill_function_columns(cols, column_names)

        # validation
        expected[1] = ["a", "w", "c", "v", "e"]
        expected[5] = ["z", "b", "y", "d", "x"]
        self.assertEqual(expected, cols)

    def testGetFileTypeConfiguration(self):
        # preparation
        column_names = ["Metadata", "FT1", "FT2", "Data type", "Function", "F_FT1", "F_FT2"]
        cols = [
            ["a", "b", "c", "d", "e"],  # column Metadata
            ["M", "O", "M", "x", "x"],  # column FT1
            ["M", "x", "x", "M", "O"],  # column FT2
            ["d", "s", "f", "b", "f"],  # column Data type (date, string, float, block, float)
            ["V", "W", "X", "Y", "Z"],  # column Function
            ["", "", "Q", "", ""],  # column F_FT1
            ["", "", "", "R", ""],  # column F_FT2
        ]

        # execution
        v.fill_function_columns(cols, column_names)
        cal_char_validator = CalCharValidator()
        cal_char_validator._REGULAR_EXPRESSION_VALID_TYPES = r"(FT1|FT2)"
        cal_char_validator._columns = cols
        cal_char_validator._col_names = column_names
        ft1_config = cal_char_validator._extractFileTypeConfigurationFor("FT1")
        ft2_config = cal_char_validator._extractFileTypeConfigurationFor("FT2")

        # validation
        expected_ft1 = {
            "File type": "FT1",
            "Mandatory": ["a", "c"],
            "Metadata": ["a", "b", "c"],
            "Data type": ["d", "s", "f"],
            "Functions": ["V", "W", "Q"]
        }
        self.assertEqual(expected_ft1, ft1_config)

        expected_ft2 = {
            "File type": "FT2",
            "Mandatory": ["a", "d"],
            "Metadata": ["a", "d", "e"],
            "Data type": ["d", "b", "f"],
            "Functions": ["V", "R", "Z"]
        }
        self.assertEqual(expected_ft2, ft2_config)


class FilenameValidationTest(unittest.TestCase):
    valid_years = ["1900", "2000", "2199"]
    valid_months = ["01", "09", "10", "12"]
    valid_days = ["01", "09", "10", "20", "29", "30", "31"]
    valid_hours = ["00", "19", "21", "23"]
    valid_min_or_sec = ["00", "12", "24", "36", "48", "59"]
    valid_endings = [".TXT"]

    valid_classes = ["CP_RAMSES_E_CLASS_", "CP_RAMSES_L_CLASS_", "CP_HYPEROCR_E_CLASS_", "CP_HYPEROCR_L_CLASS_"]
    valid_types_for_class_files = ["ANGULAR_", "POLAR_", "STRAY_", "THERMAL_"]

    valid_sam_names = ["CP_SAM_1234_", "CP_SAM_5678_", "CP_SAM_9ABC_", "CP_SAM_DF01_"]
    valid_sat_names = ["CP_SAT1234_", "CP_SAT5678_", "CP_SAT9342_"]
    valid_types_for_serial_files = ["RADCAL_", "ANGULAR_", "POLAR_", "STRAY_", "THERMAL_"]

    def testThatCalCharClassFilenamesAreValid(self):

        current_name = None

        for class_name in self.valid_classes:
            for type_name in self.valid_types_for_class_files:
                name1 = class_name + type_name
                for year in self.valid_years:
                    name2 = name1 + year
                    for month in self.valid_months:
                        name3 = name2 + month
                        for day in self.valid_days:
                            name4 = name3 + day
                            for hour in self.valid_hours:
                                name5 = name4 + hour
                                for minute in self.valid_min_or_sec:
                                    name6 = name5 + minute
                                    for second in self.valid_min_or_sec:
                                        name7 = name6 + second
                                        for ending in self.valid_endings:
                                            current_name = name7 + ending
                                            self.assertEqual(
                                                True, v.CalCharValidator.isValidFilename(current_name),
                                                f"Name '{current_name}' is expected to be valid.")

        current_name = "_" + current_name
        self.assertEqual(False, v.CalCharValidator.isValidFilename(current_name),
                         f"Name '{current_name}' is expected to be valid.")

    def testThatCalCharSerialSamFilenamesAreValid(self):

        current_name = None

        for sam_name in self.valid_sam_names:
            for type_name in self.valid_types_for_serial_files:
                name1 = sam_name + type_name
                for year in self.valid_years:
                    name2 = name1 + year
                    for month in self.valid_months:
                        name3 = name2 + month
                        for day in self.valid_days:
                            name4 = name3 + day
                            for hour in self.valid_hours:
                                name5 = name4 + hour
                                for minute in self.valid_min_or_sec:
                                    name6 = name5 + minute
                                    for second in self.valid_min_or_sec:
                                        name7 = name6 + second
                                        for ending in self.valid_endings:
                                            current_name = name7 + ending
                                            self.assertEqual(
                                                True, v.CalCharValidator.isValidFilename(current_name),
                                                f"Name '{current_name}' is expected to be valid.")

        current_name = "_" + current_name
        self.assertEqual(False, v.CalCharValidator.isValidFilename(current_name),
                         f"Name '{current_name}' is expected to be valid.")

    def testThatCalCharSerialSatFilenamesAreValid(self):
        current_name = None

        for sat_name in self.valid_sat_names:
            for type_name in self.valid_types_for_serial_files:
                name1 = sat_name + type_name
                for year in self.valid_years:
                    name2 = name1 + year
                    for month in self.valid_months:
                        name3 = name2 + month
                        for day in self.valid_days:
                            name4 = name3 + day
                            for hour in self.valid_hours:
                                name5 = name4 + hour
                                for minute in self.valid_min_or_sec:
                                    name6 = name5 + minute
                                    for second in self.valid_min_or_sec:
                                        name7 = name6 + second
                                        for ending in self.valid_endings:
                                            current_name = name7 + ending
                                            self.assertEqual(
                                                True, v.CalCharValidator.isValidFilename(current_name),
                                                f"Name '{current_name}' is expected to be valid.")

        current_name = "_" + current_name
        self.assertEqual(False, v.CalCharValidator.isValidFilename(current_name),
                         f"Name '{current_name}' is expected to be valid.")


class DeviceValidationTest(unittest.TestCase):

    def testDeviceValuesForFidraddbClassFiles(self):
        # preparation
        lines = [
            "some line content",
            "[DEVICE]",
            "wrong",
            "CLASS_HYPEROCR_IRRADIANCE"
        ]
        filename_class = "wrong class"

        # execution
        device_check_result = CalCharValidator._validate_device_value_in_class_file_content(filename_class, lines)

        # verification
        self.assertEqual(
            "Class file type 'wrong class' not known.",
            device_check_result
        )

        # preparation
        filename_class = "HYPEROCR_E_CLASS"  # valid class

        # execution
        device_check_result = CalCharValidator._validate_device_value_in_class_file_content(filename_class, lines)

        # verification
        self.assertEqual(
            "Value 'CLASS_HYPEROCR_IRRADIANCE' expected for metadata key '[DEVICE]' in file for class "
            "'HYPEROCR_E_CLASS', but found 'wrong'.",
            device_check_result
        )

        # preparation
        lines.pop(2)

        # execution
        device_check_result = CalCharValidator._validate_device_value_in_class_file_content(filename_class, lines)

        # verification
        self.assertEqual(None,  # good result
                         device_check_result)

        # preparation
        filename_class = "HYPEROCR_L_CLASS"  # valid class
        lines[2] = "CLASS_HYPEROCR_RADIANCE"

        # execution
        device_check_result = CalCharValidator._validate_device_value_in_class_file_content(filename_class, lines)

        # verification
        self.assertEqual(None,  # good result
                         device_check_result)

        # preparation
        filename_class = "RAMSES_E_CLASS"  # valid class
        lines[2] = "CLASS_RAMSES_IRRADIANCE"

        # execution
        device_check_result = CalCharValidator._validate_device_value_in_class_file_content(filename_class, lines)

        # verification
        self.assertEqual(None,  # good result
                         device_check_result)

        # preparation
        filename_class = "RAMSES_L_CLASS"  # valid class
        lines[2] = "CLASS_RAMSES_RADIANCE"

        # execution
        device_check_result = CalCharValidator._validate_device_value_in_class_file_content(filename_class, lines)

        # verification
        self.assertEqual(None,  # good result
                         device_check_result)

    def testDeviceValuesForFidraddbSerialNumberFiles(self):
        # preparation
        lines = ["some lines before",
                 "[DEVICE]",
                 "SAM_3F4C",
                 "some lines after"]

        # execution
        invalid_value_message = CalCharValidator._validate_device_value_in_serial_number_file("Different name", lines)

        # verification
        self.assertEqual("The value found in the file for the metadata key '[DEVICE]' should be equal to the "
                         "serial number 'Different name' from the file name, but 'SAM_3F4C' was found.",
                         invalid_value_message)

        # execution
        invalid_value_message = CalCharValidator._validate_device_value_in_serial_number_file("SAM_3F4C", lines)

        # verification
        self.assertEqual(None,  # good result
                         invalid_value_message)


class StaticMethodsTest(unittest.TestCase):

    def test_extract_metadata_key_information_from_lines(self):
        lines = [
            "# Some comment",
            "  ",
            "[META_KEY_1]",
            "  ",
            "[META_KEY_2]",
            "  ",
            "[END_OF_META_KEY_2]",
        ]
        information_from_file = CalCharValidator._extract_metadata_key_information_from(lines)
        expected = {
            2: "[META_KEY_1]",
            4: "[META_KEY_2]",
            6: "[END_OF_META_KEY_2]",
        }
        self.assertEqual(expected, information_from_file)

    def test_block_n_col_data__valid_result(self):
        lines = [
            "# Comment",
            "",
            "[Meta_key]",
            "{}\t{}\t{}\t{}".format(0.1, 1.2, 2.3, 3.4),
            "{}\t{}\t{}\t{}".format(4.5, 5.6, 6.7, 7.8),
            "{}\t{}\t{}\t{}".format(8.9, 9.0, 0.2, 1.3),
            "[END_OF_Meta_key]",
        ]
        info = CalCharValidator._extract_metadata_key_information_from(lines)
        keyList = list(info.keys())
        message = v.is_n_col_data(lines, keyList[0] + 1, keyList[1], ncol=4)
        self.assertEqual("", message)

    def test_block_n_col_data__with_a_single_invalid_value(self):
        lines = [
            "# Comment",
            "",
            "[Meta_key]",
            "{}\t{}\t{}\t{}".format(0.1, 1.2, 2.3, 3.4),
            "{}\t{}\t{}\t{}".format(4.5, "a", 6.7, 7.8),
            "{}\t{}\t{}\t{}".format(8.9, 9.0, 0.2, 1.3),
            "[END_OF_Meta_key]",
        ]
        info = CalCharValidator._extract_metadata_key_information_from(lines)
        keyList = list(info.keys())
        message = v.is_n_col_data(lines, keyList[0] + 1, keyList[1], ncol=4)
        self.assertEqual("Value 'a' in line 5 at pos 2 is not a valid float.", message)

    def test_block_n_col_data__line_with_less_then_expected_cols(self):
        lines = [
            "# Comment",
            "",
            "[Meta_key]",
            "{}\t{}\t{}\t{}".format(0.1, 1.2, 2.3, 3.4),
            "{}\t{}\t{}".format(4.5, 6.7, 7.8),
            "{}\t{}\t{}\t{}".format(8.9, 9.0, 0.2, 1.3),
            "[END_OF_Meta_key]",
        ]
        info = CalCharValidator._extract_metadata_key_information_from(lines)
        keyList = list(info.keys())
        message = v.is_n_col_data(lines, keyList[0] + 1, keyList[1], ncol=4)
        self.assertEqual("Line 5 contains 3 columns instead of expected 4 columns.", message)

    def test_block_n_col_data__line_with_more_then_expected_cols(self):
        lines = [
            "# Comment",
            "",
            "[Meta_key]",
            "{}\t{}\t{}\t{}".format(0.1, 1.2, 2.3, 3.4),
            "{}\t{}\t{}\t{}\t{}".format(4.5, 5.6, 6.7, 7.8, 10.0),
            "{}\t{}\t{}\t{}".format(8.9, 9.0, 0.2, 1.3),
            "[END_OF_Meta_key]",
        ]
        # execution
        info = CalCharValidator._extract_metadata_key_information_from(lines)
        # validation
        keyList = list(info.keys())
        message = v.is_n_col_data(lines, keyList[0] + 1, keyList[1], ncol=4)
        self.assertEqual("Line 5 contains 5 columns instead of expected 4 columns.", message)

    def test_keyword_check__radcal(self):
        # preparation
        lines = [
            "!FRM4SOC_CP",
            "!RADCAL",
            "",
            "some",
            "!RADCAL",
            "other",
            "lines",
            "",
            "# comment line",
        ]
        method = CalCharValidator._check_keyword_in_file_matches_the_file_type_specified_in_the_file_name

        # validation
        self.assertEqual("Keyword '!RADCAL' found 2 times but expected 1 times.", method("RADCAL", lines))
        lines.remove("!RADCAL")
        self.assertEqual(None, method("RADCAL", lines))
        lines.remove("!RADCAL")
        self.assertEqual("Keyword '!RADCAL' found 0 times but expected 1 times.", method("RADCAL", lines))

    def test_keyword_check__angdata(self):
        # preparation
        lines = [
            "!FRM4SOC_CP",
            "!ANGDATA",
            "",
            "some",
            "other",
            "lines",
            "!ANGDATA",
            "",
            "# comment line",
        ]
        method = CalCharValidator._check_keyword_in_file_matches_the_file_type_specified_in_the_file_name

        # validation
        self.assertEqual("Keyword '!ANGDATA' found 2 times but expected 1 times.", method("ANGULAR", lines))
        lines.remove("!ANGDATA")
        self.assertEqual(None, method("ANGULAR", lines))
        lines.remove("!ANGDATA")
        self.assertEqual("Keyword '!ANGDATA' found 0 times but expected 1 times.", method("ANGULAR", lines))

    def test_keyword_check__poldata(self):
        # preparation
        lines = [
            "!FRM4SOC_CP",
            "!POLDATA",
            "",
            "some",
            "other",
            "lines",
            "!POLDATA",
            "",
            "# comment line",
        ]
        method = CalCharValidator._check_keyword_in_file_matches_the_file_type_specified_in_the_file_name

        # validation
        self.assertEqual("Keyword '!POLDATA' found 2 times but expected 1 times.", method("POLAR", lines))
        lines.remove("!POLDATA")
        self.assertEqual(None, method("POLAR", lines))
        lines.remove("!POLDATA")
        self.assertEqual("Keyword '!POLDATA' found 0 times but expected 1 times.", method("POLAR", lines))

    def test_keyword_check__straydata(self):
        # preparation
        lines = [
            "!FRM4SOC_CP",
            "!STRAYDATA",
            "",
            "some",
            "other",
            "lines",
            "!STRAYDATA",
            "",
            "# comment line",
        ]
        method = CalCharValidator._check_keyword_in_file_matches_the_file_type_specified_in_the_file_name

        # validation
        self.assertEqual("Keyword '!STRAYDATA' found 2 times but expected 1 times.", method("STRAY", lines))
        lines.remove("!STRAYDATA")
        self.assertEqual(None, method("STRAY", lines))
        lines.remove("!STRAYDATA")
        self.assertEqual("Keyword '!STRAYDATA' found 0 times but expected 1 times.", method("STRAY", lines))

    def test_keyword_check__tempdata(self):
        # preparation
        lines = [
            "!FRM4SOC_CP",
            "!TEMPDATA",
            "",
            "some",
            "other",
            "lines",
            "!TEMPDATA",
            "",
            "# comment line",
        ]
        method = CalCharValidator._check_keyword_in_file_matches_the_file_type_specified_in_the_file_name

        # validation
        self.assertEqual("Keyword '!TEMPDATA' found 2 times but expected 1 times.", method("THERMAL", lines))
        lines.remove("!TEMPDATA")
        self.assertEqual(None, method("THERMAL", lines))
        lines.remove("!TEMPDATA")
        self.assertEqual("Keyword '!TEMPDATA' found 0 times but expected 1 times.", method("THERMAL", lines))
