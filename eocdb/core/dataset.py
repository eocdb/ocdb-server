from abc import ABCMeta, abstractmethod
from typing import List, Dict, Any


class Dataset(metaclass=ABCMeta):

    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """ Get the dataset's metadata header. """

    @property
    @abstractmethod
    def attribute_count(self) -> int:
        """ Get the number of attributes (columns). """

    @property
    @abstractmethod
    def attribute_names(self) -> List[str]:
        """ Get the attribute names. """

    @property
    @abstractmethod
    def record_count(self) -> int:
        """ Get the number of records (rows). """

    @property
    @abstractmethod
    def records(self) -> List[List]:
        """ Get the data records. """

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """ Get a JSON-serializable dictionary representation. """