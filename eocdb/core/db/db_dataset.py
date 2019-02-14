from typing import Dict, List

from eocdb.core.models.dataset import Dataset


class DbDataset(Dataset):

    def __init__(self,
                 metadata: Dict,
                 records: List[List[float]],
                 id_: str = None,
                 path: str = None):
        super().__init__(metadata, records, id_=id_, path=path)

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

    def add_record(self, record):
        self._records.append(record)

    def add_geo_location(self, lon, lat):
        self._longitudes.append(lon)
        self._latitudes.append(lat)

    def add_time(self, timestamp):
        self._times.append(timestamp)
