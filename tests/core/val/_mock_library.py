from eocdb.core.val._gap_aware_dict import GapAwareDict
from eocdb.core.val._message_library import MessageLibrary


class MockLibrary(MessageLibrary):

    def resolve_warning(self, template: str, tokens: GapAwareDict) -> str:
        return template

    def resolve_error(self, template: str, tokens: GapAwareDict) -> str:
        return template