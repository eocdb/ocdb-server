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


from typing import List, Union

from ..context import WsContext
from ...core.asserts import assert_not_none, assert_one_of, assert_instance
from ...core.models.dataset import Dataset
from ...core.models.dataset_query import DatasetQuery
from ...core.models.dataset_query_result import DatasetQueryResult
from ...core.models.dataset_ref import DatasetRef
from ...core.models.dataset_validation_result import DatasetValidationResult
from ...core.models.qc_info import QcInfo, QC_STATUS_SUBMITTED
from ...core.val import validator
from ...ws.errors import WsResourceNotFoundError, WsBadRequestError, WsNotImplementedError


def validate_dataset(ctx: WsContext, dataset: Dataset) -> DatasetValidationResult:
    return validator.validate_dataset(dataset, ctx.config)


def find_datasets(ctx: WsContext,
                  expr: str = None,
                  region: List[float] = None,
                  time: List[str] = None,
                  wdepth: List[float] = None,
                  mtype: str = None,
                  wlmode: str = None,
                  shallow: str = 'no',
                  pmode: str = 'contains',
                  pgroup: List[str] = None,
                  status: str = None,
                  submission_id: str = None,
                  pname: List[str] = None,
                  geojson: bool = False,
                  offset: int = 1,
                  user_id: str = None,
                  count: int = 1000) -> DatasetQueryResult:
    """Find datasets."""
    assert_one_of(shallow, ['no', 'yes', 'exclusively'], name='shallow')
    assert_one_of(pmode, ['contains', 'same_cruise', 'dont_apply'], name='pmode')
    if pgroup is not None:
        assert_instance(pgroup, [])

    # Ensuring that the search  uses lower case pnames
    if pname:
        pname = [p.lower() for p in pname]

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
    query.submission_id = submission_id
    query.status = status
    query.pname = pname
    query.geojson = geojson
    query.offset = offset
    query.count = count
    query.user_id = user_id

    result = DatasetQueryResult({}, 0, [], query)
    for driver in ctx.db_drivers:
        result_part = driver.instance().find_datasets(query)
        result.total_count += result_part.total_count
        result.datasets += result_part.datasets
        result.dataset_ids += result_part.dataset_ids
        result.locations.update(result_part.locations)

    return result


def add_dataset(ctx: WsContext,
                dataset: Dataset) -> DatasetRef:
    """Add a new dataset."""
    assert_not_none(dataset)

    validation_result = validator.validate_dataset(dataset, ctx.config)
    if validation_result.status == "ERROR":
        raise WsBadRequestError(f"Invalid dataset.")

    dataset_id = ctx.db_driver.instance().add_dataset(dataset)
    if not dataset_id:
        raise WsBadRequestError(f"Could not add dataset {dataset.path}")
    return DatasetRef(dataset_id, dataset.path, dataset.filename)


def update_dataset(ctx: WsContext,
                   dataset: Dataset):
    """Update an existing dataset."""
    assert_not_none(dataset)

    validation_result = validator.validate_dataset(dataset, ctx.config)
    if validation_result.status == "ERROR":
        raise WsBadRequestError(f"Invalid dataset.")

    updated = ctx.db_driver.instance().update_dataset(dataset)
    if not updated:
        raise WsResourceNotFoundError(f"Dataset with ID {dataset.id} not found")
    return updated


def delete_dataset(ctx: WsContext,
                   dataset_id: str):
    """Delete an existing dataset."""
    # assert_not_none(api_key, name='api_key')
    assert_not_none(dataset_id, name='dataset_id')
    deleted = ctx.db_driver.instance().delete_dataset(dataset_id)
    if not deleted:
        raise WsResourceNotFoundError(f"Dataset with ID {dataset_id} not found")
    return deleted


def get_dataset_by_id_strict(ctx: WsContext,
                             dataset_id: str) -> Dataset:
    """Get dataset by ID."""
    assert_not_none(dataset_id, name='dataset_id')
    dataset = ctx.db_driver.instance().get_dataset(dataset_id)
    if dataset is not None:
        return dataset
    raise WsResourceNotFoundError(f"Dataset with ID {dataset_id} not found")


def get_dataset_by_id(ctx: WsContext,
                      dataset_id: Union[dict, str]) -> Dataset:
    """Get dataset by ID."""
    assert_not_none(dataset_id, name='dataset_id')

    # The dataset_id may be a dataset json object
    if isinstance(dataset_id, dict):
        dataset_id = dataset_id['id']

    dataset = ctx.db_driver.instance().get_dataset(dataset_id)
    return dataset


# noinspection PyUnusedLocal,PyTypeChecker
def get_datasets_in_path(ctx: WsContext,
                         affil: str,
                         project: str,
                         cruise: str) -> List[DatasetRef]:
    assert_not_none(affil, name='affil')
    assert_not_none(project, name='project')
    assert_not_none(cruise, name='cruise')
    # TODO (generated): implement operation get_datasets_in_bucket()
    raise WsNotImplementedError('Operation get_datasets_in_bucket() not yet implemented')


# noinspection PyUnusedLocal,PyTypeChecker
def get_dataset_by_name(ctx: WsContext,
                        affil: str,
                        project: str,
                        cruise: str,
                        name: str) -> str:
    assert_not_none(affil, name='affil')
    assert_not_none(project, name='project')
    assert_not_none(cruise, name='cruise')
    assert_not_none(name, name='name')
    # TODO (generated): implement operation get_dataset_by_bucket_and_name()
    raise WsNotImplementedError('Operation get_dataset_by_bucket_and_name() not yet implemented')


# noinspection PyUnusedLocal
def get_dataset_qc_info(ctx: WsContext,
                        dataset_id: str) -> QcInfo:
    assert_not_none(dataset_id, name='dataset_id')
    dataset = ctx.db_driver.get_dataset(dataset_id)
    qc_info_dict = dataset.metadata.get("qc_info")
    return QcInfo.from_dict(qc_info_dict) if qc_info_dict else QcInfo(QC_STATUS_SUBMITTED)


# noinspection PyUnusedLocal
def set_dataset_qc_info(ctx: WsContext,
                        dataset_id: str,
                        qc_info: QcInfo):
    assert_not_none(dataset_id, name='dataset_id')
    dataset = ctx.db_driver.get_dataset(dataset_id)
    dataset.metadata["qc_info"] = qc_info.to_dict()
    ctx.db_driver.update_dataset(dataset)
