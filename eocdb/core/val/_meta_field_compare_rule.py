import operator
from datetime import datetime

import numpy as np

from eocdb.core.models import Dataset, Issue, ISSUE_TYPE_ERROR, ISSUE_TYPE_WARNING
from eocdb.core.time_helper import TimeHelper
from eocdb.core.val._rule import Rule


class MetaFieldCompareRule(Rule):

    def __init__(self, reference_name: str, compare_name: str, operation: str, error=None, warning=None):
        self._reference_name = reference_name
        self._compare_name = compare_name
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

    def eval(self, dataset: Dataset):
        metadata = dataset.metadata
        reference_value = MetaFieldCompareRule._extract_value(self._reference_name, metadata)
        if reference_value is None:
            return Issue(ISSUE_TYPE_ERROR, "Requested field not contained in metadata: " + self._reference_name)

        compare_value = MetaFieldCompareRule._extract_value(self._compare_name, metadata)
        if compare_value is None:
            return Issue(ISSUE_TYPE_ERROR, "Requested field not contained in metadata: " + self._compare_name)

        if self._operator(reference_value, compare_value):
            return None
        else:
            if self._error is not None:
                return Issue(ISSUE_TYPE_ERROR, self._error)
            if self._warning is not None:
                return Issue(ISSUE_TYPE_WARNING, self._warning)

    @staticmethod
    def _extract_value(name: str, metadata: dict):
        if not name in metadata:
            return None

        value = metadata[name]
        if "date" in name:
            converted_value = MetaFieldCompareRule._convert_date_string(value)
            return TimeHelper.parse_datetime(converted_value)

        if '[' in value:
            unit_index = value.find('[')
            value = value[0:unit_index]

        return float(value)

    @staticmethod
    def _convert_date_string(value: str) -> str:
        year = value[0:4]
        month = value[4:6]
        day = value[6:8]

        return year + "-" + month + "-" + day

