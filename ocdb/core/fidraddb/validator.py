import os
import re
from datetime import datetime
import chardet


def read_lines_split_and_strip(csv_f):
    csv = csv_f.readlines()
    for i in range(len(csv)):
        split = csv[i].split(';')
        csv[i] = split
        for j in range(len(split)):
            split[j] = split[j].strip()
    return csv


def is_valid_float(element: str) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False


def is_n_col_data(lines, start, stop, ncol=4) -> str:
    for i in range(start, stop):
        line = lines[i]
        strings = re.split("\t+", line)
        num_cols = len(strings)
        if num_cols != ncol:
            return f"Line {i +1} contains {num_cols} columns instead of expected {ncol} columns."
        for j in range(num_cols):
            val = strings[j]
            if not is_valid_float(val):
                return f"Value '{val}' in line {i + 1} at pos {j + 1} is not a valid float."
    return ""


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

    _REGULAR_EXPRESSION_VALID_TYPES = r"(ANGULAR|POLAR|RADCAL|STRAY|THERMAL)"
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
            classes_and_types = r"(RAMSES|HYPEROCR)_[EL]_CLASS_(ANGULAR|POLAR|STRAY|THERMAL)"
            serial_and_types = r"(SAM_[0-9A-F]{4}|SAT\d{4})_(ANGULAR|POLAR|RADCAL|STRAY|THERMAL)"
            class_or_serial_and_types = r"(" + classes_and_types + r"|" + serial_and_types + r")_"
            year = r"(19\d\d|2[01]\d\d)"
            month = r"(0[1-9]|1[012])"
            day = r"(0[1-9]|[12]\d|3[01])"
            hour = r"([01]\d|2[0123])"
            min_or_sec = r"[012345]\d"
            txt_ending = r"\.TXT"

            expressions = [prefix, class_or_serial_and_types, year, month, day, hour, min_or_sec, min_or_sec,
                           txt_ending]
            expression = "".join(expressions)
            # print(expression)
            cls._filename_compiled_reg_ex = re.compile(expression)

        return cls._filename_compiled_reg_ex

    def validate(self, filename: str, text: bytes) -> dict[str: str] or None:
        class_or_serial, file_type, date_time = self._split_up_filename(filename)

        valid_types = self._get_valid_types_as_list()
        if file_type not in valid_types:
            return {filename: f"Unknown filetype. Valid filetypes are {valid_types}."}

        lines = self._convert_bytes_to_lines(text)
        num_lines = len(lines)

        wrong_keyword = self._check_keyword_in_file_matches_the_file_type_specified_in_the_file_name(file_type, lines)
        if wrong_keyword:
            return {filename: wrong_keyword}

        not_same_date = self._check_same_date_time_in_filename_and_inside_file(date_time, lines)
        if not_same_date:
            return {filename: not_same_date}

        if "_CLASS" in class_or_serial:
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

        metadata_index_and_keys_in_file: dict[int, str] = self._extract_metadata_key_information_from(lines)
        list_metadata_index_in_files: list[int] = list(metadata_index_and_keys_in_file.keys())
        list_metadata_keys_in_files: list[str] = list(metadata_index_and_keys_in_file.values())
        all_keys_in_file = [x for x in list_metadata_keys_in_files if not x.startswith("[END_OF_")]

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

        metadata_types: list[str] = type_info.get(self.__KEY_DATA_TYPE)
        val_functions: list[str] = type_info.get(self.__KEY_FUNCTION)

        for i in range(len(allowed_keys)):
            meta_name: str = allowed_keys[i]
            metadata_type: str = metadata_types[i]
            val_function: str = val_functions[i]

            braced_meta_name: str = "[" + meta_name + "]"
            braced_end_name = "[END_OF_" + meta_name + "]"

            braced_meta_count = list_metadata_keys_in_files.count(braced_meta_name)
            braced_end_count = list_metadata_keys_in_files.count(braced_end_name)

            if metadata_type.lower() == "block":
                times_opened = braced_meta_count
                times_closed = braced_end_count
                if times_opened != times_closed:
                    return {filename: f"There is something wrong with the file. The section {braced_meta_name} was "
                                      f"opened {times_opened} times but closed {times_closed} times."}

            if braced_meta_count == 0:
                continue  # this is the case if an optional metadata key is not present

            if meta_name == "CALDATE":
                continue  # already checked
            elif meta_name == "DEVICE":
                continue  # already checked ... see lines after the line --> if "_class" in class_or_serial.lower():
            elif metadata_type == "str":
                keys_list_start_idx = 0
                for j in range(braced_meta_count):
                    list_idx = list_metadata_keys_in_files.index(braced_meta_name, keys_list_start_idx)
                    keys_list_start_idx = list_idx + 1
                    start_line = list_metadata_index_in_files[list_idx] + 1
                    if start_line < num_lines:
                        value = lines[start_line]
                        if value is not None and value.strip():
                            # print("is not None and not empty")
                            continue
                    return {filename: f"Value for {braced_meta_name} is missing"}
            elif metadata_type == "float":
                keys_list_start_idx = 0
                for j in range(braced_meta_count):
                    list_idx = list_metadata_keys_in_files.index(braced_meta_name, keys_list_start_idx)
                    keys_list_start_idx = list_idx + 1
                    start_line = list_metadata_index_in_files[list_idx] + 1
                    if start_line >= num_lines:
                        return {filename: f"Float value for {braced_meta_name} is missing"}
                    value = lines[start_line]
                    if is_valid_float(value):
                        continue
                    return {filename: f"Float value for {braced_meta_name} is not a float"}
            elif metadata_type == "block":
                keys_list_start_idx = 0
                ncols_start = val_function.index("ncol=") + 5
                ncols_end = val_function.index(")", ncols_start)
                ncols = int(val_function[ncols_start:ncols_end])
                for j in range(braced_meta_count):
                    list_idx = list_metadata_keys_in_files.index(braced_meta_name, keys_list_start_idx)
                    keys_list_start_idx = list_idx + 1
                    start_line = list_metadata_index_in_files[list_idx] + 1
                    end_line = list_metadata_index_in_files[list_idx + 1]
                    result = is_n_col_data(lines, start_line, end_line, ncols)
                    if result:
                        return {filename: f"Col check for {braced_meta_name}. {result}"}
        return None

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
        # lines = [x for x in lines if not x.startswith("#")]  # removes comment lines but keeps empty lines
        # lines = [x for x in lines if not x.startswith("#") or x != ""]  # removes comment lines and empty lines
        return lines

    @staticmethod
    def _extract_metadata_key_information_from(lines) -> dict[int, str]:
        idx = -1
        all_keys_in_file = {}
        for line in lines:
            idx += 1
            if line.startswith("["):
                all_keys_in_file.update({idx: line})

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
        if filename_class not in known_classes:
            return f"Class file type '{filename_class}' not known."

        expected_value = known_classes.get(filename_class)

        key = "[DEVICE]"
        dev_index = lines.index(key)
        val_index = dev_index + 1
        value = lines[val_index]
        if expected_value != value.upper():
            return f"Value '{expected_value}' expected for metadata key '{key}' in file for " \
                   f"class '{filename_class}', but found '{value}'."

    @staticmethod
    def _validate_device_value_in_serial_number_file(filename_serial_number: str, lines: list[str]) -> str or None:
        key = "[DEVICE]"
        dev_index = lines.index(key)
        val_index = dev_index + 1
        value = lines[val_index]

        if filename_serial_number != value.upper():
            return f"The value found in the file for the metadata key '{key}' should be equal to the " \
                   f"serial number '{filename_serial_number}' from the file name, but '{value}' was found."

    @staticmethod
    def _check_keyword_in_file_matches_the_file_type_specified_in_the_file_name(file_type, lines) -> str or None:
        # Get all lines that begin with an exclamation mark.
        extract = [x for x in lines if x and x.startswith("!")]

        expected_counts = [
            ("!RADCAL", 1 if file_type == "RADCAL" else 0),
            ("!ANGDATA", 1 if file_type == "ANGULAR" else 0),
            ("!POLDATA", 1 if file_type == "POLAR" else 0),
            ("!STRAYDATA", 1 if file_type == "STRAY" else 0),
            ("!TEMPDATA", 1 if file_type == "THERMAL" else 0),
        ]

        for _tuple in expected_counts:
            keyword = _tuple[0]
            expected_count = _tuple[1]
            count = extract.count(keyword)
            if count != expected_count:
                return f"Keyword '{keyword}' found {count} times but expected {expected_count} times."
