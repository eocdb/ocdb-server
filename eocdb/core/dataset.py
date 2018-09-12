import datetime
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

    @property
    @abstractmethod
    def geo_locations(self) -> List[List]:
        """ Get the geo-location for the records. """

    @property
    @abstractmethod
    def times(self) -> List[datetime.datetime]:
        """ Get the acquisition times for the records. """

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """ Get a JSON-serializable dictionary representation. """