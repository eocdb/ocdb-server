from abc import abstractmethod
from typing import Optional

from eocdb.core.models import Dataset, Issue


class Rule():

    @abstractmethod
    def eval(self, dataset: Dataset) -> Optional[Issue]:
        """Apply the rule to the dataset and eventually return an issue"""
