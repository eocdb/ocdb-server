from abc import abstractmethod
from typing import List

from eocdb.core import Service, Dataset
from eocdb.core.deprecated import deprecated


class DbDriver(Service):

    @abstractmethod
    @deprecated
    def get(self, query_expression=None) -> List[Dataset]:
        """Query database for list of datasets matching the query_expression"""

    @abstractmethod
    @deprecated
    def insert(self, document):
        """Insert one document into database"""
