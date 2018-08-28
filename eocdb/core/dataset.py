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

    @classmethod
    def from_dict(cls, obj: Dict[str, Any]) -> 'Dataset':
        """ Turn a JSON-serializable dictionary *obj* into a Dataset. """
        return DictBackedDataset(obj)


# noinspection PyAbstractClass
class DictBackedDataset(Dataset):
    def __init__(self, obj: Dict[str, Any]):
        self._obj = obj

    @property
    def metadata(self) -> Dict[str, Any]:
        if 'metadata' in self._obj:
            return self._obj['metadata']
        return {}

    @property
    def attribute_count(self) -> int:
        if 'attribute_count' in self._obj:
            return self._obj['attribute_count']
        if 'attribute_names' in self._obj:
            return len(self._obj['attribute_names'])
        return 0

    @property
    def attribute_names(self) -> List[str]:
        if 'attribute_names' in self._obj:
            return self._obj['attribute_names']
        return []

    @property
    def record_count(self) -> int:
        if 'record_count' in self._obj:
            return self._obj['record_count']
        if 'records' in self._obj:
            return len(self._obj['records'])
        return 0

    @property
    def records(self) -> List[List]:
        if 'records' in self._obj:
            return self._obj['records']
        return []

    def to_dict(self) -> Dict[str, Any]:
        return self._obj
