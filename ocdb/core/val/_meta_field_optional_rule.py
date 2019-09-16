from ocdb.core.models import Dataset, Issue, ISSUE_TYPE_WARNING
from ocdb.core.val._gap_aware_dict import GapAwareDict
from ocdb.core.val._message_library import MessageLibrary
from ocdb.core.val._rule import Rule


class MetaFieldOptionalRule(Rule):

    def __init__(self, name: str, warning: str):
        self._name = name
        self._warning = warning

    def eval(self, dataset: Dataset, library: MessageLibrary):
        if not self._name in dataset.metadata:
            return None

        value = dataset.metadata[self._name]
        if len(value) > 0:
            return None
        else:
            message_dict = GapAwareDict({"reference": self._name})
            warning_message = library.resolve_warning(self._warning, message_dict)
            return Issue(ISSUE_TYPE_WARNING, warning_message)