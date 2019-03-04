from eocdb.core.models import Dataset, Issue, ISSUE_TYPE_ERROR
from eocdb.core.val._gap_aware_dict import GapAwareDict
from eocdb.core.val._message_library import MessageLibrary
from eocdb.core.val._rule import Rule


class MetaFieldRequiredRule(Rule):

    def __init__(self, name: str, error: str):
        self._name = name
        self._error = error

    def eval(self, dataset: Dataset, library: MessageLibrary):
        if not self._name in dataset.metadata:
            return self.create_error_message(library)

        value = dataset.metadata[self._name]
        value = str(value)
        if len(value) > 0:
            return None
        else:
            return self.create_error_message(library)

    def create_error_message(self, library):
        message_dict = GapAwareDict({"reference": self._name})
        error_message = library.resolve_error(self._error, message_dict)
        return Issue(ISSUE_TYPE_ERROR, error_message)