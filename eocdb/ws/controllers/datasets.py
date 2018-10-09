from typing import List

from ..context import WsContext
from ..models.api_response import ApiResponse
from ..models.dataset import Dataset
from ..models.dataset_query_result import DatasetQueryResult
from ..models.dataset_ref import DatasetRef


def find_datasets(ctx: WsContext,
                  expr: str = None, region: List[float] = None, time: List[str] = None,
                  wdepth: List[float] = None, mtype: str = None, wlmode: str = None, shallow: str = None,
                  pmode: str = None, pgroup: List[str] = None, pname: List[str] = None, offset: int = None,
                  count: int = None) -> DatasetQueryResult:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation find_datasets() not yet implemented')


def update_dataset(ctx: WsContext, data: Dataset) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation update_dataset() not yet implemented')


def add_dataset(ctx: WsContext, data: Dataset) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation add_dataset() not yet implemented')


def get_dataset_by_id(ctx: WsContext, id_: str) -> Dataset:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation get_dataset_by_id() not yet implemented')


def delete_dataset(ctx: WsContext, id_: str, api_key: str = None) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation delete_dataset() not yet implemented')


def get_datasets_in_bucket(ctx: WsContext, affil: str, project: str, cruise: str) -> List[DatasetRef]:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation get_datasets_in_bucket() not yet implemented')


def get_dataset_by_bucket_and_name(ctx: WsContext, affil: str, project: str, cruise: str, name: str) -> str:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation get_dataset_by_bucket_and_name() not yet implemented')
