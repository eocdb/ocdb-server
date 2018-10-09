from typing import List, Dict

from ..context import WsContext
from ..models.api_response import ApiResponse


def get_store_info(ctx: WsContext) -> Dict:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation get_store_info() not yet implemented')


def upload_store_files(ctx: WsContext, data: Dict) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation upload_store_files() not yet implemented')


def download_store_files(ctx: WsContext,
                         expr: str = None, region: List[float] = None, time: List[str] = None,
                         wdepth: List[float] = None, mtype: str = None, wlmode: str = None, shallow: str = None,
                         pmode: str = None, pgroup: List[str] = None, pname: List[str] = None,
                         docs: bool = None) -> str:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation download_store_files() not yet implemented')
