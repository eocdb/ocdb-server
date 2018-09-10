from typing import Dict, Any, List

from eocdb.core.dataset import Dataset


class DbDataset(Dataset):

    def __init__(self):
        self._records = []
        self._attributes = []
        self._geo_locations = []
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
    def attributes(self) -> List[str]:
        return self._attributes

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

    def geo_locations(self) -> List[List]:
        return self._geo_locations

    def add_geo_location(self, lon, lat):
        self._geo_locations.append({'lon' : lon, 'lat': lat})

    def to_dict(self) -> Dict[str, Any]:
        return {'records': self._records}
