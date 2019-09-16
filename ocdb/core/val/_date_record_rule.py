from datetime import datetime
from typing import List, Optional

from ocdb.core.models import Issue, ISSUE_TYPE_ERROR, ISSUE_TYPE_WARNING
from ocdb.core.val._gap_aware_dict import GapAwareDict
from ocdb.core.val._message_library import MessageLibrary


class DateRecordRule:

    @staticmethod
    def from_dict(value_dict: dict):
        name = value_dict["name"]
        min_year = value_dict["min_year"]

        return DateRecordRule(name, min_year)

    def __init__(self, name: str, min_year: int):
        self._name = name
        self._min_year = min_year

    def eval(self, unit: str, values: List[str], library: MessageLibrary, missing_value: float = None) -> Optional[List[Issue]]:
        empty = ""
        issues = []

        index = 0
        for value in values:
            value = str(value)
            index += 1
            if value is empty:
                self._append_error_issue("@data_invalid_date", index, issues, library)
                continue

            if len(value) != 8:
                self._append_error_issue("@data_invalid_date", index, issues, library)
                continue

            try:
                year = int(value[0:4])
                month = int(value[4:6])
                day = int(value[6:8])
            except:
                self._append_error_issue("@data_invalid_date", index, issues, library)
                continue

            if year < self._min_year:
                self._append_error_issue("@data_date_bounds_error", index, issues, library)
                continue

            if month > 12 or month < 1:
                self._append_error_issue("@data_invalid_month", index, issues, library)

            if day > 31 or day < 1:
                self._append_error_issue("@data_invalid_day_of_month", index, issues, library)

        if len(issues) > 0:
            return issues

        return None

    def _append_error_issue(self, message, index, issues, library):
        error_message = self._assemble_error_message(index, library, message)
        issues.append(Issue(ISSUE_TYPE_ERROR, error_message))

    def _append_warning_issue(self, message, index, issues, library):
        error_message = self._assemble_error_message(index, library, message)
        issues.append(Issue(ISSUE_TYPE_WARNING, error_message))

    def _assemble_error_message(self, index, library, message):
        today = datetime.today()
        lower_bound = datetime(self._min_year, 1, 1, 0, 0, 0)
        message_dict = GapAwareDict(
            {"field_name": self._name, "line": index, "lower_bound": str(lower_bound), "upper_bound": str(today)})
        error_message = library.resolve_error(message, message_dict)
        return error_message

    @property
    def name(self) -> str:
        return self._name

    @property
    def min_year(self) -> int:
        return self._min_year
