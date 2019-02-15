import csv
import fnmatch
import json
import os
from typing import List, Any, Dict

Field = Dict[str, Any]
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
_PRODUCT_TO_GROUP = None
_WILDCARD_PRODUCT_TO_GROUP = None


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

def get_groups_for_product(product) -> List[str]:
    """
        Return a list of product groups names the product passed in belongs to.
        May return empty list.
        """
    global _PRODUCT_TO_GROUP
    global _WILDCARD_PRODUCT_TO_GROUP

    if _PRODUCT_TO_GROUP is None:
        _load_product_to_group_map()

    if product in _PRODUCT_TO_GROUP:
        return _PRODUCT_TO_GROUP[product]

    for wc_product in _WILDCARD_PRODUCT_TO_GROUP:
        if fnmatch.fnmatch(product, wc_product):
            return _WILDCARD_PRODUCT_TO_GROUP[wc_product]

    return []


def _load_product_to_group_map():
    global _PRODUCT_TO_GROUP
    _PRODUCT_TO_GROUP = {}

    global _WILDCARD_PRODUCT_TO_GROUP
    _WILDCARD_PRODUCT_TO_GROUP = {}

    product_groups = get_product_groups()
    for product_group in product_groups:
        for product in product_group["products"]:
            if "*" in product or "?" in product:
                if not product in _WILDCARD_PRODUCT_TO_GROUP:
                    _WILDCARD_PRODUCT_TO_GROUP.update({product: [product_group["name"]]})
                else:
                    _WILDCARD_PRODUCT_TO_GROUP[product].append(product_group["name"])
            else:
                if not product in _PRODUCT_TO_GROUP:
                    _PRODUCT_TO_GROUP.update({product: [product_group["name"]]})
                else:
                    _PRODUCT_TO_GROUP[product].append(product_group["name"])


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
                name = row[0]
                groups = get_groups_for_product(name)
                _FIELDS.append(dict(name=name, units=row[1], description=row[2], groups=groups))
    return _FIELDS
