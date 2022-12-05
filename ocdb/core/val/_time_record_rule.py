import re
from typing import List, Optional

from ocdb.core.models import Issue, ISSUE_TYPE_ERROR
from ocdb.core.val._gap_aware_dict import GapAwareDict
from ocdb.core.val._message_library import MessageLibrary


class TimeRecordRule:

    @staticmethod
    def from_dict(value_dict: dict):
        name = value_dict["name"]
        unit = value_dict["unit"]
        error = value_dict["unit_error"]

        return TimeRecordRule(name, unit, error)

    def __init__(self, name: str, unit: str, error: str):
        self._name = name
        self._time_string_pattern = re.compile(r"\d{2}:\d{2}:\d{2}")
        self._hour_range = range(0, 24)
        self._min_sec_range = range(0, 60)
        self._units = unit.lower().split(",")
        self._unit_error = error

    def eval(self, unit: str, values: List[str], library: MessageLibrary, missing_value: float = None) -> Optional[
        List[Issue]]:
        issues = []

        if unit not in self._units:
            message_dict = GapAwareDict({"field_name": self._name, "unit": self._units, "bad_unit": unit})
            error_message = library.resolve_error(self._unit_error, message_dict)
            issues.append(Issue(ISSUE_TYPE_ERROR, error_message))

        index = 0
        for value in values:
            index +=1
            message_dict = GapAwareDict({"field_name": self._name, "line": index})
            if not self._time_string_pattern.match(value):
                error_message = library.resolve_error("@invalid_time_record", message_dict)
                issues.append(Issue(ISSUE_TYPE_ERROR, error_message))
                continue

            tokens = value.split(":")
            hour = int(tokens[0])
            minute = int(tokens[1])
            second = int(tokens[2])

            if hour not in self._hour_range \
                    or minute not in self._min_sec_range \
                    or second not in self._min_sec_range:
                error_message = library.resolve_error("@invalid_time_value", message_dict)
                issues.append(Issue(ISSUE_TYPE_ERROR, error_message))
                continue

        if len(issues) > 0:
            return issues

        return None

    @property
    def name(self):
        return self._name

    @property
    def unit(self):
        return self._units

    @property
    def unit_error(self):
        return self._unit_error
