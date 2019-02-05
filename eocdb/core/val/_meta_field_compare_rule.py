import operator

from eocdb.core.models import Dataset, Issue, ISSUE_TYPE_ERROR, ISSUE_TYPE_WARNING
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
        if self._reference_name in dataset.metadata:
            reference_value = dataset.metadata[self._reference_name]
            if '[' in reference_value:
                unit_index = reference_value.find('[')
                reference_value = reference_value[0:unit_index]
        else:
            return Issue(ISSUE_TYPE_ERROR, "Requested field not contained in metadata: " + self._reference_name)

        ref = float(reference_value)

        if self._compare_name in dataset.metadata:
            compare_value = dataset.metadata[self._compare_name]
            if '[' in compare_value:
                unit_index = compare_value.find('[')
                compare_value = compare_value[0:unit_index]
        else:
            return Issue(ISSUE_TYPE_ERROR, "Requested field not contained in metadata: " + self._compare_name)

        comp = float(compare_value)

        if self._operator(ref, comp):
            return None
        else:
            if self._error is not None:
                return Issue(ISSUE_TYPE_ERROR, self._error)
            if self._warning is not None:
                return Issue(ISSUE_TYPE_WARNING, self._warning)