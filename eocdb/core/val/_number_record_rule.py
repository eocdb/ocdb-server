from typing import Optional, List

from eocdb.core.models import Issue, ISSUE_TYPE_ERROR
from eocdb.core.val._gap_aware_dict import GapAwareDict
from eocdb.core.val._message_library import MessageLibrary


class NumberRecordRule():

    def __init__(self, name: str, unit: str, unit_error: str, value_error: str, lower_bound: float = None, upper_bound: float = None):
        self._name = name
        self._unit = unit
        self._unit_error = unit_error
        self._value_error = value_error
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

    def eval(self, unit: str, values: List[float], library: MessageLibrary) -> Optional[List[Issue]]:
        issues = []

        if unit != self._unit:
            message_dict = GapAwareDict({"field_name": self._name, "unit": self._unit, "bad_unit": unit})
            error_message = library.resolve_error(self._unit_error, message_dict)
            issues.append(Issue(ISSUE_TYPE_ERROR, error_message))

        line = 0
        message_dict = GapAwareDict({"field_name": self._name,
                                     "line": line,
                                     "value": 0,
                                     "lower_bound": self._lower_bound,
                                     "upper_bound": self._upper_bound})

        for value in values:
            out_of_bounds = False
            if self._lower_bound is not None:
                if value < self._lower_bound:
                    out_of_bounds = True

            if self._upper_bound is not None:
                if value > self._upper_bound:
                    out_of_bounds = True

            if out_of_bounds:
                message_dict["line"] = line
                message_dict["value"] = value
                error_message = library.resolve_error(self._value_error, message_dict)
                issues.append(Issue(ISSUE_TYPE_ERROR, error_message))

            line += 1

        if len(issues) > 0:
            return issues

        return None
