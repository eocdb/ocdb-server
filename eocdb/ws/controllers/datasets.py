# The MIT License (MIT)
# Copyright (c) 2018 by EUMETSAT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import List

from ..context import WsContext
from ...core.models.dataset import Dataset
from ...core.models.dataset_query import DatasetQuery
from ...core.models.dataset_query_result import DatasetQueryResult
from ...core.models.dataset_ref import DatasetRef
from ...core.models.dataset_validation_result import DatasetValidationResult
from ...core.val import validator
from ...ws.errors import WsResourceNotFoundError, WsBadRequestError, WsNotImplementedError


# noinspection PyUnusedLocal
def validate_dataset(ctx: WsContext, dataset: Dataset) -> DatasetValidationResult:
    return validator.validate_dataset(dataset)


def find_datasets(ctx: WsContext, expr: str = None, region: List[float] = None, time: List[str] = None,
                  wdepth: List[float] = None, mtype: str = None, wlmode: str = None, shallow: str = None,
                  pmode: str = None, pgroup: List[str] = None, pname: List[str] = None, offset: int = None,
                  count: int = None) -> DatasetQueryResult:
    query = DatasetQuery()
    query.expr = expr
    query.region = region
    query.time = time
    query.wdepth = wdepth
    query.mtype = mtype
    query.wlmode = wlmode
    query.shallow = shallow
    query.pmode = pmode
    query.pgroup = pgroup
    query.pname = pname
    query.offset = offset
    query.count = count

    result = DatasetQueryResult()
    result.query = query
    result.total_count = 0
    result.datasets = []

    for driver in ctx.get_db_drivers(mode="r"):
        result_part = driver.instance().find_datasets(query)
        result.total_count += result_part.total_count
        result.datasets += result_part.datasets

    return result


def add_dataset(ctx: WsContext, dataset: Dataset):
    validation_result = validator.validate_dataset(dataset)
    if validation_result.status == "ERROR":
        raise WsBadRequestError(f"Invalid dataset.")
    added = False
    for driver in ctx.get_db_drivers(mode="w"):
        if driver.instance().add_dataset(dataset):
            added = True
    if not added:
        raise WsBadRequestError(f"Could not add dataset {dataset.name}")


def update_dataset(ctx: WsContext, dataset: Dataset):
    validation_result = validator.validate_dataset(dataset)
    if validation_result.status == "ERROR":
        raise WsBadRequestError(f"Invalid dataset.")
    updated = False
    for driver in ctx.get_db_drivers(mode="w"):
        if driver.instance().update_dataset(dataset):
            updated = True
    if not updated:
        raise WsResourceNotFoundError(f"Dataset with ID {dataset.id} not found")


# noinspection PyUnusedLocal
def delete_dataset(ctx: WsContext, dataset_id: str, api_key: str = None):
    deleted = False
    for driver in ctx.get_db_drivers(mode="w"):
        if driver.instance().delete_dataset(dataset_id):
            deleted = True
    if not deleted:
        raise WsResourceNotFoundError(f"Dataset with ID {dataset_id} not found")


def get_dataset_by_id(ctx: WsContext, dataset_id: str) -> Dataset:
    for driver in ctx.get_db_drivers(mode="r"):
        dataset = driver.instance().get_dataset(dataset_id)
        if dataset is not None:
            return dataset
    raise WsResourceNotFoundError(f"Dataset with ID {dataset_id} not found")


# noinspection PyUnusedLocal
def get_datasets_in_bucket(ctx: WsContext, affil: str, project: str, cruise: str) -> List[DatasetRef]:
    raise WsNotImplementedError('Operation get_datasets_in_bucket() not yet implemented')


# noinspection PyUnusedLocal
def get_dataset_by_bucket_and_name(ctx: WsContext, affil: str, project: str, cruise: str, name: str) -> str:
    raise WsNotImplementedError('Operation get_dataset_by_bucket_and_name() not yet implemented')
