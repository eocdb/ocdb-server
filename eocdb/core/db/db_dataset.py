import datetime
from typing import Dict, Any, List

from eocdb.core.dataset import Dataset


class DbDataset(Dataset):

    def __init__(self):
        self._records = []
        self._attributes = []
        self._geo_locations = []
        self._times = []
        self._metadata = dict()

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata

    def set_metadata(self, metadata):
        self._metadata = metadata

    def add_metadatum(self, key, value):
        self._metadata.update({key: value})

    @property
    def attribute_count(self) -> int:
        return len(self._attributes)

    @property
    def attribute_names(self) -> List[str]:
        return self._attributes

    def add_attributes(self, attribute_names):
        self._attributes.extend(attribute_names)

    @property
    def record_count(self) -> int:
        return len(self._records)

    @property
    def records(self) -> List[List]:
        return self._records

    def add_record(self, record):
        self._records.append(record)

    @property
    def geo_locations(self) -> List[List]:
        return self._geo_locations

    def add_geo_location(self, lon, lat):
        self._geo_locations.append({'lon': lon, 'lat': lat})

    @property
    def times(self) -> List[datetime.datetime]:
        return self._times

    def add_time(self, timestamp):
        self._times.append(timestamp)

    def to_dict(self) -> Dict[str, Any]:
        result_dict = dict()
        result_dict.update({'metadata': self.metadata})
        result_dict.update({'records': self._records})
        result_dict.update({'attributes': self._attributes})
        result_dict.update({'geo_locations': self._geo_locations})
        converted_times = []
        for time in self._times:
            converted_times.append(time.isoformat())
        result_dict.update({'times': converted_times})
        return result_dict
