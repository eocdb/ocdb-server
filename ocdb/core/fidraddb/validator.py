import os
import re
from datetime import datetime
from typing import Any, Tuple

import chardet


def read_lines_split_and_strip(csv_f):
    csv = csv_f.readlines()
    for i in range(len(csv)):
        split = csv[i].split(';')
        csv[i] = split
        for j in range(len(split)):
            split[j] = split[j].strip()
    return csv


def transpose_list_per_row_to_list_per_column(csv: list or None):
    ensure_is_a_list_of_lists(csv)

    columns = list(zip(*csv))
    for j in range(len(columns)):
        columns[j] = list(columns[j])
    return columns


def ensure_is_a_list_of_lists(list_obj):
    type_error = TypeError("list of lists expected")
    if not isinstance(list_obj, list):
        raise type_error

    for item in list_obj:
        if not isinstance(item, list):
            raise type_error


def fill_function_columns(columns: list[list], colum_names: list[str]):
    cols_to_be_filled = []
    for columName in colum_names:
        if columName.strip().startswith("F_"):
            cols_to_be_filled.append(colum_names.index(columName))
    function_column = columns[colum_names.index("Function")]
    for i in cols_to_be_filled:
        current_column = columns[i]
        for j in range(len(current_column)):
            if current_column[j] == '':
                current_column[j] = function_column[j]


class CalCharValidator:
    __KEY_FILETYPENAME = "File type"
    __KEY_FUNCTION = "Functions"
    __KEY_DATA_TYPE = "Data type"
    __KEY_METADATA = "Metadata"
    __KEY_MANDATORY = "Mandatory"

    _REGULAR_EXPRESSION_VALID_TYPES = r"(angular|polar|radcal|stray|thermal)"
    _filename_compiled_reg_ex: re.Pattern = None

    def __init__(self) -> None:
        super().__init__()
        self._columns = None
        self._col_names = []
        path_to_csv_configuration_file = os.path.join(os.path.dirname(__file__), "res", "CalChar_Validation.CSV")
        with open(path_to_csv_configuration_file) as csv_f:
            self._initialize(csv_f)

    def _initialize(self, csv_f):
        csv = read_lines_split_and_strip(csv_f)
        self._col_names = csv.pop(0)
        cols = transpose_list_per_row_to_list_per_column(csv)
        fill_function_columns(cols, self._col_names)
        self._columns = cols

    @classmethod
    def isValidFilename(cls, filename: str):
        full_match = cls._getCompiledFileNameExpression().fullmatch(filename)
        return full_match is not None

    @classmethod
    def _getCompiledFileNameExpression(cls) -> re.Pattern:
        if cls._filename_compiled_reg_ex is None:
            prefix = r"CP_"
            classes_and_types = r"(RAMSES|HyperOCR)_[EL]_class_(ANGULAR|POLAR|STRAY|THERMAL)"
            serial_and_types = r"(SAM_[0-9A-Fa-f]{4}|SAT\d{4})_(ANGULAR|POLAR|RADCAL|STRAY|THERMAL)"
            class_or_serial_and_types = r"(" + classes_and_types + r"|" + serial_and_types + r")_"
            year = r"(19\d\d|2[01]\d\d)"
            month = r"(0[1-9]|1[012])"
            day = r"(0[1-9]|[12]\d|3[01])"
            hour = r"([01]\d|2[0123])"
            min_or_sec = r"[012345]\d"
            txt_ending = r"\.txt"

            expressions = [prefix, class_or_serial_and_types, year, month, day, hour, min_or_sec, min_or_sec,
                           txt_ending]
            expression = "".join(expressions)
            # print(expression)
            cls._filename_compiled_reg_ex = re.compile(expression, re.IGNORECASE)

        return cls._filename_compiled_reg_ex

    def validate(self, filename: str, text: bytes) -> dict[str: str] or None:
        class_or_serial, file_type, date_time = self._split_up_filename(filename)

        valid_types = self._get_valid_types_as_list()
        if file_type not in valid_types:
            return {filename: f"Unknown filetype. Valid filetypes are {valid_types}."}

        lines = self._convert_bytes_to_lines(text)
        not_same_date = self._check_same_date_time_in_filename_and_inside_file(date_time, lines)
        if not_same_date:
            return {filename: not_same_date}

        if "_class" in class_or_serial:
            filename_class = class_or_serial
            invalid_value_message = self._validate_device_value_in_class_file_content(filename_class, lines)
            if invalid_value_message:
                return {filename: invalid_value_message}
        else:
            serial_number = class_or_serial
            invalid_value_message = self._validate_device_value_in_serial_number_file(serial_number, lines)
            if invalid_value_message:
                return {filename: invalid_value_message}
            type_info = self._extractFileTypeConfigurationFor(file_type)

            all_keys_in_file: list[str] = self._extract_existing_keys_from_file(lines)

            # check if all mandatory metadata names are present in the file
            mandatory_keys: list[str] = type_info.get(self.__KEY_MANDATORY)
            missing_result = self._find_missing_mandatory_keys(mandatory_keys, all_keys_in_file, filename)
            if missing_result:
                return missing_result

            # check if all metadata keys, extracted from file, are present in the list of allowed keys
            allowed_keys: list[str] = type_info.get(self.__KEY_METADATA)
            unexpected_result = self._find_unexpected_metadata_keys(allowed_keys, all_keys_in_file, filename)
            if unexpected_result:
                return unexpected_result

            for i in range(len(allowed_keys)):
                meta_name: str = allowed_keys[i]
                braced_meta_name: str = "[" + meta_name + "]"

                occurrences: list[int] = self._find_occurrences(braced_meta_name, lines)

                is_mandatory: bool = meta_name in mandatory_keys
                # count_min: int = 1 if is_mandatory else 0

                current_type: str = type_info.get(self.__KEY_DATA_TYPE)[i]

                braced_end_name = None
                end_occurrences = None
                if current_type.lower() == "block":
                    braced_end_name = "[END_OF_" + braced_meta_name[1:]
                    end_occurrences = self._find_occurrences(braced_end_name, lines)
                    times_opened = len(occurrences)
                    times_closed = len(end_occurrences)
                    if times_opened != times_closed:
                        return {filename: f"There is something wrong with the file. The section {braced_meta_name} was "
                                          f"opened {times_opened} times but closed {times_closed} times."}

                if len(occurrences) == 0:
                    continue  # this is the case if an optional metadata key is not present

                if meta_name == "CALDATE":
                    pass  # already checked
                elif meta_name == "DEVICE":
                    oc_idx = occurrences[0]
                    val = lines[oc_idx + 1]

                elif meta_name == "CALLAB":
                    pass
                elif meta_name == "USER":
                    pass
                elif meta_name == "VERSION":
                    pass
                elif meta_name == "CALDATA":
                    pass
                elif meta_name == "UNCERTAINTY":
                    pass
                elif meta_name == "COSERROR":
                    pass
                elif meta_name == "LSF":
                    pass
                elif meta_name == "PANEL_ID":
                    pass
                elif meta_name == "LAMP_ID":
                    pass
                elif meta_name == "AZIMUTH_ANGLE":
                    pass
                elif meta_name == "LAMP_CCT":
                    pass
                elif meta_name == "AMBIENT_TEMP":
                    pass
                elif meta_name == "REFERENCE_TEMP":
                    pass
                elif meta_name == "PANELDATA":
                    pass
                elif meta_name == "LAMPDATA":
                    pass

        return None

    @staticmethod
    def _find_occurrences(braced_meta_name, lines) -> list[int]:
        indices = []
        start = 0
        for n in range(lines.count(braced_meta_name)):
            idx = lines.index(braced_meta_name, start)
            start = idx + 1
            indices.append(idx)
        return indices

    def _get_valid_types_as_list(self) -> list:
        return self._REGULAR_EXPRESSION_VALID_TYPES[1:-1].split("|")

    @staticmethod
    def _check_same_date_time_in_filename_and_inside_file(date_time_from_file_name, lines) -> str or None:
        index = lines.index("[CALDATE]")
        date_time_from_inside_file = lines[index + 1]
        datetime_1 = datetime.strptime(date_time_from_file_name, "%Y%m%d%H%M%S")
        datetime_2 = datetime.strptime(date_time_from_inside_file, "%Y-%m-%d %H:%M:%S")
        if datetime_1 != datetime_2:
            return f"The date time in the filename is not equal to the " \
                   f"date inside the file {date_time_from_inside_file}."

    def _split_up_filename(self, filename: str) -> tuple[str, str, str]:
        re_types = self._REGULAR_EXPRESSION_VALID_TYPES
        split = re.split(re_types, filename, flags=re.IGNORECASE)
        class_or_serial: str = split[0][3:-1]
        file_type: str = split[1]
        date_time_from_file_name: str = split[2][1:-4]
        return class_or_serial, file_type, date_time_from_file_name

    @staticmethod
    def _convert_bytes_to_lines(text):
        txt_encoding = chardet.detect(text)['encoding']
        text = text.decode(txt_encoding)
        lines = re.split('(\n\r|\r\n|\n|\r)', text)  # also returns the split characters
        separators = ['\n', '\r', '\n\r', '\r\n']
        lines = [x.strip() for x in lines if x not in separators]  # removes the separators and strip the lines
        lines = [x for x in lines if not x.startswith("#") or x != ""]  # removes comment lines and empty lines
        return lines

    @staticmethod
    def _extract_existing_keys_from_file(lines):
        all_keys_in_file = [x for x in lines if x.startswith("[")]
        all_keys_in_file = [x for x in all_keys_in_file if not x.startswith("[END_OF_")]
        return all_keys_in_file

    @staticmethod
    def _find_missing_mandatory_keys(mandatory_keys: list[str], all_keys_in_file: list[str], filename: str) -> dict:
        for key in mandatory_keys:
            key = "[" + key + "]"
            if key not in all_keys_in_file:
                return {filename: f"The metadata key '{key}' must be included in this file."}

    @staticmethod
    def _find_unexpected_metadata_keys(allowed_keys: list[str], all_keys_in_file: list[str], filename: str) -> dict:
        for key in all_keys_in_file:
            key_name = key.replace("[", "").replace("]", "")  # remove braces
            if key_name not in allowed_keys:
                return {filename: f"The metadata key '{key}' is not expected."}

    def _extractFileTypeConfigurationFor(self, file_type: str):
        type_index: int = self._get_valid_types_as_list().index(file_type)
        csv_type: str = self._col_names[type_index + 1]

        file_type_column: list = self._columns[self._col_names.index(csv_type)].copy()
        mandatory: list[str] = []
        metadata_column: list[str] = self._columns[self._col_names.index("Metadata")].copy()
        data_type_column: list[str] = self._columns[self._col_names.index("Data type")].copy()
        functions_column: list[str] = self._columns[self._col_names.index("F_" + csv_type)].copy()

        for i in reversed(range(len(file_type_column))):
            mandatory_optional_or_excluded: str = file_type_column[i]
            if mandatory_optional_or_excluded == "x":
                metadata_column.pop(i)
                data_type_column.pop(i)
                functions_column.pop(i)
            elif mandatory_optional_or_excluded == "M":
                mandatory.append(metadata_column[i])

        mandatory.reverse()
        return {
            self.__KEY_FILETYPENAME: csv_type,
            self.__KEY_MANDATORY: mandatory,
            self.__KEY_METADATA: metadata_column,
            self.__KEY_DATA_TYPE: data_type_column,
            self.__KEY_FUNCTION: functions_column
        }

    @staticmethod
    def _validate_device_value_in_class_file_content(filename_class: str, lines: list[str]) -> str or None:
        known_classes = {
            "HYPEROCR_E_CLASS": "CLASS_HYPEROCR_IRRADIANCE",
            "HYPEROCR_L_CLASS": "CLASS_HYPEROCR_RADIANCE",
            "RAMSES_E_CLASS": "CLASS_RAMSES_IRRADIANCE",
            "RAMSES_L_CLASS": "CLASS_RAMSES_RADIANCE"
        }
        filename_class_upper = filename_class.upper()
        if filename_class_upper not in known_classes:
            return f"Class file type '{filename_class}' not known."

        expected_value = known_classes.get(filename_class_upper)

        key = "[DEVICE]"
        dev_index = lines.index(key)
        val_index = dev_index + 1
        value = lines[val_index]
        if expected_value != value.upper():
            return f"Value '{expected_value}' expected for metadata key '{key}' in file for " \
                   f"class '{filename_class}', but found '{value}'."

    @staticmethod
    def _validate_device_value_in_serial_number_file(filename_serial_number: str, lines: list[str]) -> str or None:
        expected_value = filename_serial_number.upper()

        key = "[DEVICE]"
        dev_index = lines.index(key)
        val_index = dev_index + 1
        value = lines[val_index]

        if expected_value != value.upper():
            return f"The value found in the file for the metadata key '{key}' should be equal to the " \
                   f"serial number '{filename_serial_number}' from the file name, but '{value}' was found."

