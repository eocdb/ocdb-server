from ..context import WsContext
from ..models.api_response import ApiResponse
from ..models.user import User


def create_user(ctx: WsContext, data: User) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation create_user() not yet implemented')


def login_user(ctx: WsContext, username: str = None, password: str = None) -> str:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation login_user() not yet implemented')


def logout_user(ctx: WsContext) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation logout_user() not yet implemented')


def get_user_by_id(ctx: WsContext, id_: int) -> User:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation get_user_by_id() not yet implemented')


def update_user(ctx: WsContext, id_: int, data: User) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation update_user() not yet implemented')


def delete_user(ctx: WsContext, id_: int) -> ApiResponse:
    # return dict(code=200, status='OK')
    raise NotImplementedError('operation delete_user() not yet implemented')
