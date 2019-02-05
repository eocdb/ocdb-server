from eocdb.core.models import Dataset, Issue, ISSUE_TYPE_WARNING
from eocdb.core.val._rule import Rule


class MetaFieldOptionalRule(Rule):

    def __init__(self, name: str, warning: str):
        self._name = name
        self._warning = warning

    def eval(self, dataset: Dataset):
        if not self._name in dataset.metadata:
            return None

        value = dataset.metadata[self._name]
        if len(value) > 0:
            return None
        else:
            return Issue(ISSUE_TYPE_WARNING, self._warning)