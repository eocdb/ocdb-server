from eocdb.core.models import Dataset, Issue, ISSUE_TYPE_ERROR
from eocdb.core.val._rule import Rule


class MetaFieldRequiredRule(Rule):

    def __init__(self, name: str, error: str):
        self._name = name
        self._error = error

    def eval(self, dataset: Dataset):
        if not self._name in dataset.metadata:
            return Issue(ISSUE_TYPE_ERROR, self._error)

        value = dataset.metadata[self._name]
        if len(value) > 0:
            return None
        else:
            return Issue(ISSUE_TYPE_ERROR, self._error)