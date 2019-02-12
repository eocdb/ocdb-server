from ...core.val._gap_aware_dict import GapAwareDict
from ...core.models import Dataset, Issue, ISSUE_TYPE_WARNING
from ...core.val._message_library import MessageLibrary
from ...core.val._rule import Rule


class MetaFieldObsoleteRule(Rule):

    def __init__(self, name: str, warning: str):
        self._name = name
        self._warning = warning

    def eval(self, dataset: Dataset, library: MessageLibrary):
        if self._name in dataset.metadata:
            message_dict = GapAwareDict({"reference": self._name})
            warning_message = library.resolve_warning(self._warning, message_dict)
            return Issue(ISSUE_TYPE_WARNING, warning_message)

        return None