from abc import abstractmethod

from ocdb.core.val._gap_aware_dict import GapAwareDict


class MessageLibrary:

    @abstractmethod
    def resolve_warning(self, template: str, tokens: GapAwareDict) -> str:
        """Returns a ready-to-print warning message"""

    @abstractmethod
    def resolve_error(self, template: str, tokens: GapAwareDict) -> str:
        """Returns a ready-to-print error message"""
