import operator

from eocdb.core.models import Dataset, Issue, ISSUE_TYPE_ERROR, ISSUE_TYPE_WARNING
from eocdb.core.time_helper import TimeHelper
from eocdb.core.val._gap_aware_dict import GapAwareDict
from eocdb.core.val._message_library import MessageLibrary
from eocdb.core.val._rule import Rule


class MetaFieldCompareRule(Rule):

    def __init__(self, reference_name: str, compare_name: str, operation: str, data_type: str, error=None, warning=None):
        self._reference_name = reference_name
        self._compare_name = compare_name
        self._data_type = data_type
        self._error = error
        self._warning = warning

        if operation == ">=":
            self._operator = operator.ge
        elif operation == ">":
            self._operator = operator.gt
        elif operation == "!=":
            self._operator = operator.ne
        elif operation == "==":
            self._operator = operator.eq
        elif operation == "<":
            self._operator = operator.lt
        elif operation == "<=":
            self._operator = operator.le
        else:
            raise ValueError("operator is not valid: " + operation)

    def eval(self, dataset: Dataset, library: MessageLibrary):
        metadata = dataset.metadata
        reference_value = self._extract_value(self._reference_name, metadata)
        if reference_value is None:
            return Issue(ISSUE_TYPE_ERROR, "Requested field not contained in metadata: " + self._reference_name)

        compare_value = self._extract_value(self._compare_name, metadata)
        if compare_value is None:
            return Issue(ISSUE_TYPE_ERROR, "Requested field not contained in metadata: " + self._compare_name)

        if self._operator(reference_value, compare_value):
            return None
        else:
            message_dict = GapAwareDict({"reference": self._reference_name, "ref_val": reference_value, "compare": self._compare_name, "comp_val": compare_value})
            if self._error is not None:
                error_message = library.resolve_error(self._error, message_dict)
                return Issue(ISSUE_TYPE_ERROR, error_message)
            if self._warning is not None:
                warning_message = library.resolve_warning(self._warning, message_dict)
                return Issue(ISSUE_TYPE_WARNING, warning_message)

    def _extract_value(self, name: str, metadata: dict):
        if not name in metadata:
            return None

        value = metadata[name]
        if self._data_type == "date" in name:
            converted_value = MetaFieldCompareRule._convert_date_string(value)
            return TimeHelper.parse_datetime(converted_value)

        if self._data_type == "number":
            if '[' in value:
                unit_index = value.find('[')
                value = value[0:unit_index]

            return float(value)

        if self._data_type == "string":
            return value

        raise ValueError("Invalid data_type for rule: " + self._data_type)

    @staticmethod
    def _convert_date_string(value: str) -> str:
        year = value[0:4]
        month = value[4:6]
        day = value[6:8]

        return year + "-" + month + "-" + day
