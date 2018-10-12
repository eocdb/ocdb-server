import csv
import json
import os
from typing import List, Any, Dict

Field = Dict[str, str]
ProductGroup = Dict[str, Any]

_NON_PRODUCT_FIELD_NAMES = {
    "day",
    "hour",
    "lat",
    "lon",
    "minute",
    "month",
    "sdy",
    "second",
    "time",
    "year",
}

_FIELDS = None
_PRODUCT_GROUPS = None


def get_product_groups() -> List[ProductGroup]:
    """
    Return a list of product groups of the form
    ``dict(name=<product-group-name>, units=<units>, description=<description>)``.
    """
    global _PRODUCT_GROUPS
    if _PRODUCT_GROUPS is None:
        file = os.path.join(os.path.dirname(__file__), "res", "product-groups.json")
        with open(file, encoding="utf8") as fp:
            _PRODUCT_GROUPS = json.load(fp)
    return _PRODUCT_GROUPS


def get_products() -> List[Field]:
    """
    Return a list of allowed and valid product names of the form
    ``dict(name=<product-group-name>, description=<description>, products=<products>)``, where
    <products> is a list of the form ``[<field-wildcard>, <field-wildcard>, <field-wildcard>, ...]``.

    This is a filtered version of the list returned by func::get_fields.
    """
    return [f for f in get_fields() if f["name"] not in _NON_PRODUCT_FIELD_NAMES]


def get_fields() -> List[Field]:
    """
    Return a list of allowed and valid field names of the form
    ``[<field-wildcard>, <units>, <description>]``.

    A "field" refers to a column name
    """
    global _FIELDS
    if _FIELDS is None:
        _FIELDS = []
        file = os.path.join(os.path.dirname(__file__), "res", "fields.csv")
        with open(file, encoding="utf8") as fp:
            reader = csv.reader(fp, delimiter=';')
            for row in reader:
                if len(row) != 3:
                    raise ValueError(f"malformed file {file}, rows must have 3 columns")
                _FIELDS.append(dict(name=row[0], units=row[1], description=row[2]))
    return _FIELDS
