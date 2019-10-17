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
               password: str,
               retain_password: bool = False) -> Dict[str, str]:

    #if 'mode' in ctx.config and ctx.config['mode'] == 'dev':
    #    return ctx.get_user('chef').to_dict()

    assert_not_none(username, name='username')
    assert_not_none(password, name='password')

    user = ctx.get_user(username, password)
    if not user:
        raise WsUnauthorizedError("Unknown username or password")

    user = user.to_dict()
    if not retain_password:
        del user['password']

    return user


# noinspection PyUnusedLocal
def create_user(ctx: WsContext,
                user: User):
    user_test = ctx.get_user(user.name)
    if user_test is not None:
        raise WsBadRequestError(f"User exists:  {user.name}")

    user_id = ctx.db_driver.instance().add_user(user)
    if not user_id:
        raise WsBadRequestError(f"Could not add user {user.name}")

    return user_id


# noinspection PyUnusedLocal,PyTypeChecker
def get_user_by_name(ctx: WsContext,
                     user_name: str,
                     retain_password: bool = False) -> User:
    assert_not_none(user_name, name='user_id')

    user = ctx.get_user(user_name)
    if not user:
        raise WsBadRequestError(f"Could not find user {user_name}")

    user_dict = user.to_dict()
    if not retain_password:
        del user_dict['password']
    return user_dict


def get_user_names(ctx: WsContext):
    return ctx.db_driver.get_user_names()


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
