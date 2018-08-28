from typing import Dict, Any, List

from eocdb.core.dataset import Dataset


class DbDataset(Dataset):

    def __init__(self):
        self._records = []

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict()

    @property
    def attribute_count(self) -> int:
        return 0

    @property
    def attribute_names(self) -> List[str]:
        return []

    @property
    def record_count(self) -> int:
        return len(self._records)

    @property
    def records(self) -> List[List]:
        return self._records

    def add_record(self, record):
        self._records.append(record)

    def to_dict(self) -> Dict[str, Any]:
        return {'records' : self._records}
