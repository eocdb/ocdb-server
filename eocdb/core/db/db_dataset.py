import datetime
from typing import Dict, Any, List

from eocdb.core.models.dataset import Dataset


class DbDataset(Dataset):

    def __init__(self,
                 metadata: Dict,
                 records: List[List[float]],
                 id_: str = None,
                 path: str = None):
        super().__init__(metadata, records, id_=id_, path=path)
        self._attributes = []
        self._times = []

    def add_metadatum(self, key, value):
        self._metadata.update({key: value})

    @property
    def attribute_count(self) -> int:
        return len(self._attributes)

    @property
    def attributes(self) -> List:
        return self._attributes

    @property
    def attribute_names(self) -> List[str]:
        return self._attributes

    def set_attributes(self, attributes):
        self._attributes = attributes

    def add_attributes(self, attribute_names):
        self._attributes.extend(attribute_names)

    @property
    def record_count(self) -> int:
        return len(self._records)

    def add_record(self, record):
        self._records.append(record)

    def add_geo_location(self, lon, lat):
        self._longitudes.append(lon)
        self._latitudes.append(lat)

    @property
    def times(self) -> List[datetime.datetime]:
        return self._times

    def add_time(self, timestamp):
        self._times.append(timestamp)

    def to_dict(self) -> Dict[str, Any]:
        result_dict = super().to_dict()
        converted_times = []
        for time in self._times:
            converted_times.append(time.isoformat())
        result_dict.update({'times': converted_times})
        return result_dict
