from typing import List

from ..context import WsContext


def add_doc_file(ctx: WsContext):
    # TODO: implement operation addDocFile
    return dict(code=200, status='OK')


def update_doc_file(ctx: WsContext):
    # TODO: implement operation updateDocFile
    return dict(code=200, status='OK')


def get_doc_files_in_bucket(ctx: WsContext, affil: str, project: str, cruise: str):
    # TODO: implement operation getDocFilesInBucket
    return dict(code=200, status='OK')


def download_doc_file(ctx: WsContext, affil: str, project: str, cruise: str, name: str):
    # TODO: implement operation downloadDocFile
    return dict(code=200, status='OK')


def delete_doc_file(ctx: WsContext, affil: str, project: str, cruise: str, name: str):
    # TODO: implement operation deleteDocFile
    return dict(code=200, status='OK')
