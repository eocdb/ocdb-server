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


from typing import Optional, List

from ..asserts import assert_not_none
from ..model import Model


class User(Model):
    """
    The User model.
    """

    def __init__(self,
                 name: str,
                 password: str,
                 first_name: str,
                 last_name: str,
                 email: str,
                 phone: str,
                 roles: List[str]):
        assert_not_none(name, name='name')
        assert_not_none(first_name, name='first_name')
        assert_not_none(last_name, name='last_name')
        assert_not_none(email, name='email')
        assert_not_none(password, name='password')
        assert_not_none(phone, name='phone')
        assert_not_none(roles, name='roles')
        self._name = name
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._password = password
        self._phone = phone
        self._roles = roles

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        assert_not_none(value, name='value')
        self._name = value

    @property
    def first_name(self) -> Optional[str]:
        return self._first_name

    @first_name.setter
    def first_name(self, value: Optional[str]):
        assert_not_none(value, name='value')
        self._first_name = value

    @property
    def last_name(self) -> Optional[str]:
        return self._last_name

    @last_name.setter
    def last_name(self, value: Optional[str]):
        assert_not_none(value, name='value')
        self._last_name = value

    @property
    def email(self) -> Optional[str]:
        return self._email

    @email.setter
    def email(self, value: Optional[str]):
        assert_not_none(value, name='value')
        self._email = value

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str):
        assert_not_none(value, name='value')
        self._password = value

    @property
    def phone(self) -> Optional[str]:
        return self._phone

    @phone.setter
    def phone(self, value: Optional[str]):
        assert_not_none(value, name='value')
        self._phone = value

    @property
    def roles(self) -> Optional[List[str]]:
        return self._roles

    @roles.setter
    def roles(self, value: Optional[List[str]]):
        assert_not_none(value, name='value')
        self._roles = value
