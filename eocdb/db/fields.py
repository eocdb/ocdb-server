import csv
import os
from typing import Tuple, List

Field = Tuple[str, str, str]

_FIELDS = None


def get_fields() -> List[Field]:
    global _FIELDS
    if _FIELDS is None:
        _FIELDS = []
        file = os.path.join(os.path.dirname(__file__), "res", "fields.csv")
        with open(file) as fp:
            reader = csv.reader(fp, delimiter=';', )
            for row in reader:
                _FIELDS.append(row)
    return _FIELDS
