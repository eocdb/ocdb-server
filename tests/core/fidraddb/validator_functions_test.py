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
    valid_endings = [".tXt", ".TxT"]

    valid_classes = ["Cp_RaMsEs_E_cLaSs_", "cP_rAmSeS_l_ClAsS_", "CP_HyperOCR_E_class_", "CP_HyperOCR_L_class_"]
    valid_types_for_class_files = ["AnGuLaR_", "PoLaR_", "StRaY_", "ThErMaL_"]

    valid_sam_names = ["Cp_SaM_1234_", "Cp_SaM_5678_", "Cp_SaM_9aBc_", "Cp_SaM_Df01_"]
    valid_sat_names = ["Cp_SaT1234_", "Cp_sAt5678_", "Cp_SaT9342_"]
    valid_types_for_serial_files = ["RaDcAl_", "AnGuLaR_", "PoLaR_", "StRaY_", "ThErMaL_"]

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

                                            current_name_upper = current_name.upper()
                                            self.assertEqual(
                                                True, v.CalCharValidator.isValidFilename(current_name_upper),
                                                f"Name '{current_name_upper}' is expected to be valid.")

                                            current_name_lower = current_name.lower()
                                            self.assertEqual(
                                                True, v.CalCharValidator.isValidFilename(current_name_lower),
                                                f"Name '{current_name_lower}' is expected to be valid.")

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

                                            current_name_upper = current_name.upper()
                                            self.assertEqual(
                                                True, v.CalCharValidator.isValidFilename(current_name_upper),
                                                f"Name '{current_name_upper}' is expected to be valid.")

                                            current_name_lower = current_name.lower()
                                            self.assertEqual(
                                                True, v.CalCharValidator.isValidFilename(current_name_lower),
                                                f"Name '{current_name_lower}' is expected to be valid.")

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

                                            current_name_upper = current_name.upper()
                                            self.assertEqual(
                                                True, v.CalCharValidator.isValidFilename(current_name_upper),
                                                f"Name '{current_name_upper}' is expected to be valid.")

                                            current_name_lower = current_name.lower()
                                            self.assertEqual(
                                                True, v.CalCharValidator.isValidFilename(current_name_lower),
                                                f"Name '{current_name_lower}' is expected to be valid.")

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
        filename_class = "HyperOCR_E_class"  # valid class

        # execution
        device_check_result = CalCharValidator._validate_device_value_in_class_file_content(filename_class, lines)

        # verification
        self.assertEqual(
            "Value 'CLASS_HYPEROCR_IRRADIANCE' expected for metadata key '[DEVICE]' in file for class "
            "'HyperOCR_E_class', but found 'wrong'.",
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
        filename_class = "HyperOCR_L_class"  # valid class
        lines[2] = "CLASS_HYPEROCR_RADIANCE"

        # execution
        device_check_result = CalCharValidator._validate_device_value_in_class_file_content(filename_class, lines)

        # verification
        self.assertEqual(None,  # good result
                         device_check_result)

        # preparation
        filename_class = "RAMSES_E_class"  # valid class
        lines[2] = "CLASS_RAMSES_IRRADIANCE"

        # execution
        device_check_result = CalCharValidator._validate_device_value_in_class_file_content(filename_class, lines)

        # verification
        self.assertEqual(None,  # good result
                         device_check_result)

        # preparation
        filename_class = "RAMSES_L_class"  # valid class
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
