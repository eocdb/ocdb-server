from typing import List

from ..context import WsContext


def find_datasets(ctx: WsContext, expr: str = None, region: List = None, time: List = None, wdepth: List = None, mtype: str = 'all', wlmode: str = 'all', shallow: str = 'no', pmode: str = 'contains', pgroup: List = None, pname: List = None, offset: int = 1, count: int = 1000):
    # TODO: implement operation findDatasets
    return dict(code=200, status='OK')


def update_dataset(ctx: WsContext):
    # TODO: implement operation updateDataset
    return dict(code=200, status='OK')


def add_dataset(ctx: WsContext):
    # TODO: implement operation addDataset
    return dict(code=200, status='OK')


def get_dataset_by_id(ctx: WsContext, id: str):
    # TODO: implement operation getDatasetById
    return dict(code=200, status='OK')


def delete_dataset(ctx: WsContext, id: int):
    # TODO: implement operation deleteDataset
    return dict(code=200, status='OK')


def get_datasets_in_bucket(ctx: WsContext, affil: str, project: str, cruise: str):
    # TODO: implement operation getDatasetsInBucket
    return dict(code=200, status='OK')


def get_dataset_by_bucket_and_name(ctx: WsContext, affil: str, project: str, cruise: str, name: str):
    # TODO: implement operation getDatasetByBucketAndName
    return dict(code=200, status='OK')
