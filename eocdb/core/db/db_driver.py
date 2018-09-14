from abc import abstractmethod
from typing import List

from eocdb.core import Service, Dataset


class DbDriver(Service):

    @abstractmethod
    def get(self, query_expression=None) -> List[Dataset]:
        """Query database for list of datasets matching the query_expression"""

    @abstractmethod
    def insert(self, document):
        """Insert one document into database"""
