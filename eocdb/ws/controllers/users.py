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
from typing import Dict

from ..context import WsContext
from ..errors import WsUnauthorizedError, WsBadRequestError
from ...core.asserts import assert_not_none
from ...core.models.user import User


# noinspection PyUnusedLocal,PyTypeChecker
def login_user(ctx: WsContext,
               username: str,
               password: str) -> Dict[str, str]:
    assert_not_none(username, name='username')
    assert_not_none(password, name='password')

    user = ctx.db_driver.instance().get_user(username, password)

    if not user:
        raise WsUnauthorizedError("Unknown username or password")

    user = user.to_dict()

    del user['password']

    return user

    # users = ctx.config.get("users")
    # if not users:
    #     raise WsNotImplementedError("No users configured")
    # if not isinstance(users, list):
    #     raise WsNotImplementedError("Invalid user configuration")
    # for user in users:
    #     if not isinstance(user, dict):
    #         raise WsUnauthorizedError("Invalid user configuration")
    # for user in users:
    #     if user.get("name") == username or user.get("email") == username:
    #         actual_password = user.get('password')
    #         if actual_password == password:
    #             user = dict(**user)
    #             del user['password']
    #             return user
    #         else:
    #             break


# noinspection PyUnusedLocal
def create_user(ctx: WsContext,
                user: User):
    user_id = ctx.db_driver.instance().add_user(user)

    if not user_id:
        raise WsBadRequestError(f"Could not add user {user.name}")

    return user_id


# noinspection PyUnusedLocal
def logout_user(ctx: WsContext,
                user_id: int):
    # TODO (generated): implement operation logout_user()
    raise NotImplementedError('operation logout_user() not yet implemented')


# noinspection PyUnusedLocal,PyTypeChecker
def get_user_by_name(ctx: WsContext,
                     user_name: str) -> User:
    assert_not_none(user_name, name='user_id')

    user = ctx.db_driver.instance().get_user(user_name)

    if not user:
        raise WsBadRequestError(f"Could not find user {user_name}")

    # users = ctx.config['users']
    #
    # user = None
    # for u in users:
    #     if u['id'] == user_id:
    #         user = u

    user_dict = user.to_dict()
    del user_dict['password']
    return user_dict


# noinspection PyUnusedLocal,PyTypeChecker
def check_user_by_name(ctx: WsContext,
                       user_name: str) -> User:
    assert_not_none(user_name, name='user_id')

    user = ctx.db_driver.instance().get_user(user_name)

    if not user:
        return False
    else:
        return True


# noinspection PyUnusedLocal
def update_user(ctx: WsContext,
                user_name: str,
                data: User):
    assert_not_none(user_name, name='user_name')
    updated = ctx.db_driver.instance().update_user(data)

    if not updated:
        raise WsBadRequestError(f"Could not update user {data.name}")

    return updated


# noinspection PyUnusedLocal
def delete_user(ctx: WsContext,
                user_name: str):
    assert_not_none(user_name, name='user_name')
    deleted = ctx.db_driver.instance().delete_user(user_name)

    if not deleted:
        raise WsBadRequestError(f"Could not delete user {user_name}")

    return deleted
