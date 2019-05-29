from abc import abstractmethod
from typing import Optional

from ...core.models import Dataset, Issue
from ...core.val._message_library import MessageLibrary


class Rule:

    @abstractmethod
    def eval(self, dataset: Dataset, library: MessageLibrary) -> Optional[Issue]:
        """Apply the rule to the dataset and eventually return an issue"""
