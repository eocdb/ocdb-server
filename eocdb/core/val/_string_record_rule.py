from typing import List, Optional

from eocdb.core.models import Issue, ISSUE_TYPE_ERROR
from eocdb.core.val._gap_aware_dict import GapAwareDict
from eocdb.core.val._message_library import MessageLibrary


class StringRecordRule:

    @staticmethod
    def from_dict(value_dict: dict):
        name = value_dict["name"]
        error = value_dict["error"]

        return StringRecordRule(name, error)

    def __init__(self, name: str, error: str):
        self._name = name
        self._error = error

    def eval(self, unit: str, values: List[str], library: MessageLibrary) -> Optional[List[Issue]]:
        empty = ""
        issues = []

        index = 1
        for value in values:
            if value is empty:
                message_dict = GapAwareDict({"field_name": self._name, "line": index})
                error_message = library.resolve_error(self._error, message_dict)
                issues.append(Issue(ISSUE_TYPE_ERROR, error_message))
            index += 1

        if len(issues) > 0:
            return issues

        return None

    @property
    def name(self):
        return self._name

    @property
    def error(self):
        return self._error
