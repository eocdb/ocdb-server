import math
from typing import Optional, List

from ocdb.core.models import Issue, ISSUE_TYPE_ERROR
from ocdb.core.val._gap_aware_dict import GapAwareDict
from ocdb.core.val._message_library import MessageLibrary

no_units: List[str] = ["none", "unitless"]


class NumberRecordRule:

    @staticmethod
    def from_dict(value_dict: dict):
        name = value_dict["name"]
        unit = value_dict["unit"]

        if "unit_error" in value_dict:
            unit_error = value_dict["unit_error"]
        else:
            unit_error = None

        if "value_error" in value_dict:
            value_error = value_dict["value_error"]
        else:
            value_error = None

        lower_bound = NumberRecordRule._extract_lower_bound(value_dict)
        upper_bound = NumberRecordRule._extract_upper_bound(value_dict)

        return NumberRecordRule(name, unit, unit_error, value_error, lower_bound, upper_bound)

    @staticmethod
    def _extract_lower_bound(value_dict):
        if "lower_bound" in value_dict:
            lower_str = value_dict["lower_bound"]
            lower_bound = float(lower_str)
        else:
            lower_bound = float('-inf')
        return lower_bound

    @staticmethod
    def _extract_upper_bound(value_dict):
        if "upper_bound" in value_dict:
            upper_str = value_dict["upper_bound"]
            upper_bound = float(upper_str)
        else:
            upper_bound = float('+inf')
        return upper_bound

    def __init__(self, name: str, unit: str, unit_error: str, value_error: str, lower_bound: float = float('nan'),
                 upper_bound: float = float('nan')):
        self._name = name

        if unit in no_units:
            self._units = no_units
        else:
            self._units = unit.lower().split(",")

        self._unit_error = unit_error
        self._value_error = value_error
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

    def eval(self, unit: str, values: List[float], library: MessageLibrary,
             missing_value: float = None) -> Optional[List[Issue]]:
        issues = []

        if unit not in self._units:
            message_dict = GapAwareDict({"field_name": self._name, "unit": self._units, "bad_unit": unit})
            error_message = library.resolve_error(self._unit_error, message_dict)
            issues.append(Issue(ISSUE_TYPE_ERROR, error_message))

        line = 1
        message_dict = GapAwareDict({"field_name": self._name,
                                     "line": line,
                                     "value": 0,
                                     "lower_bound": self._lower_bound,
                                     "upper_bound": self._upper_bound})

        for value in values:
            out_of_bounds = False
            if not (type(value) is float or type(value) is int):
                message_dict["line"] = line
                message_dict["value"] = value
                error_message = library.resolve_error("@field_number_not_a_number", message_dict)
                issues.append(Issue(ISSUE_TYPE_ERROR, error_message))
                line += 1
                continue

            if missing_value is not None and value == missing_value:
                line += 1
                continue

            if not math.isnan(self._lower_bound):
                if value < self._lower_bound:
                    out_of_bounds = True

            if not math.isnan(self._upper_bound):
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

    @property
    def name(self) -> str:
        return self._name

    @property
    def units(self) -> List[str]:
        return self._units

    @property
    def unit_error(self) -> str:
        return self._unit_error

    @property
    def value_error(self) -> str:
        return self._value_error

    @property
    def lower_bound(self) -> float:
        return self._lower_bound

    @property
    def upper_bound(self) -> float:
        return self._upper_bound
