from typing import List, Dict

from ..models.api_response import ApiResponse
from ..models.doc_file_ref import DocFileRef
from ..context import WsContext


def add_doc_file(ctx: WsContext, data: Dict) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation add_doc_file() not yet implemented')


def update_doc_file(ctx: WsContext, data: Dict) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation update_doc_file() not yet implemented')


def get_doc_files_in_bucket(ctx: WsContext, affil: str, project: str, cruise: str) -> List[DocFileRef]:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation get_doc_files_in_bucket() not yet implemented')


def download_doc_file(ctx: WsContext, affil: str, project: str, cruise: str, name: str) -> str:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation download_doc_file() not yet implemented')


def delete_doc_file(ctx: WsContext, affil: str, project: str, cruise: str, name: str) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation delete_doc_file() not yet implemented')
