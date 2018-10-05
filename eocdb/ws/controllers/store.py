from typing import List

from ..context import WsContext


def get_store_info(ctx: WsContext):
    # TODO: implement operation getStoreInfo
    return dict(code=200, status='OK')


def upload_store_files(ctx: WsContext, file_path: str):
    # TODO: implement operation uploadStoreFiles
    return dict(code=200, status='OK')


def download_store_files(ctx: WsContext, expr: str = None, region: List = None, time: List = None, wdepth: List = None, mtype: str = 'all', wlmode: str = 'all', shallow: str = 'no', pmode: str = 'contains', pgroup: List = None, pname: List = None, docs: bool = False):
    # TODO: implement operation downloadStoreFiles
    return dict(code=200, status='OK')
