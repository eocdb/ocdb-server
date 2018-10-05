from typing import List

from ..context import WsContext


def create_user(ctx: WsContext):
    # TODO: implement operation createUser
    return dict(code=200, status='OK')


def login_user(ctx: WsContext, username: str, password: str):
    # TODO: implement operation loginUser
    return dict(code=200, status='OK')


def logout_user(ctx: WsContext):
    # TODO: implement operation logoutUser
    return dict(code=200, status='OK')


def get_user_by_id(ctx: WsContext, id: int):
    # TODO: implement operation getUserByID
    return dict(code=200, status='OK')


def update_user(ctx: WsContext, id: int):
    # TODO: implement operation updateUser
    return dict(code=200, status='OK')


def delete_user(ctx: WsContext, id: int):
    # TODO: implement operation deleteUser
    return dict(code=200, status='OK')
