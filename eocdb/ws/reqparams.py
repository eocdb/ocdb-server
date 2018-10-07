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

from abc import abstractmethod, ABCMeta
from typing import Optional, List

from .errors import WsBadRequestError


class RequestParams(metaclass=ABCMeta):
    @classmethod
    def to_bool(cls, name: str, value: str) -> bool:
        """
        Convert str value to int.
        :param name: Name of the value
        :param value: The string value
        :return: The int value
        :raise: WsBadRequestError
        """
        if value is None:
            raise WsBadRequestError(f'value for parameter "{name!r}" must be a boolean, but none was given')
        try:
            value = value.lower()
            if value == 'true':
                return True
            if value == 'false':
                return False
            return bool(int(value))
        except ValueError as e:
            raise WsBadRequestError(f'value for parameter "{name!r}" must be a boolean, but was {value!r}') from e

    @classmethod
    def to_int(cls,
               name: str,
               value: str,
               minimum: int = None,
               maximum: int = None) -> int:
        """
        Convert str value to int.
        :param name: Name of the value
        :param value: The string value
        :param minimum: Optional minimum value
        :param maximum: Optional maximum value
        :return: The int value
        :raise: WsBadRequestError
        """
        if value is None:
            raise WsBadRequestError(f'value for parameter "{name!r}" must be an integer, but none was given')
        try:
            value = int(value)
            if minimum is not None and value < minimum:
                raise WsBadRequestError(f'value of "{name!r}" must not be < {minimum}, but was {value!r}')
            if maximum is not None and value > maximum:
                raise WsBadRequestError(f'value of "{name!r}" must not be > {maximum}, but was {value!r}')
            return value
        except ValueError as e:
            raise WsBadRequestError(f'"value for parameter {name!r}" must be an integer, but was {value!r}') from e

    @classmethod
    def to_float(cls,
                 name: str,
                 value: str,
                 minimum: float = None,
                 maximum: float = None) -> float:
        """
        Convert str value to float.
        :param name: Name of the value
        :param value: The string value
        :param minimum: Optional minimum value
        :param maximum: Optional maximum value
        :param value: The string value
        :return: The float value
        :raise: WsBadRequestError
        """
        if value is None:
            raise WsBadRequestError(f'value for parameter "{name!r}" must be a number, but none was given')
        try:
            value = float(value)
            if minimum is not None and value < minimum:
                raise WsBadRequestError(f'value for parameter "{name!r}" must not be < {minimum}, but was {value!r}')
            if maximum is not None and value > maximum:
                raise WsBadRequestError(f'value for parameter "{name!r}" must not be > {maximum}, but was {value!r}')
            return value
        except ValueError as e:
            raise WsBadRequestError(f'value for parameter "{name!r}" must be a number, but was {value!r}') from e

    @classmethod
    def to_list(cls,
                name: str,
                value: str) -> List[str]:
        """
        Convert str value to int array.
        :param name: Name of the value
        :param value: The string value
        :return: The int value
        :raise: WsBadRequestError
        """
        if value is not None:
            value = list(value.split(','))
        if value is None or value == ['']:
            raise WsBadRequestError(f'value for parameter "{name!r}" must be a list, but none was given')
        return value

    @classmethod
    def to_int_list(cls,
                    name: str,
                    value: str,
                    minimum: int = None,
                    maximum: int = None) -> List[int]:
        """
        Convert str value to int array.
        :param name: Name of the value
        :param value: The string value
        :param minimum: Optional minimum value
        :param maximum: Optional maximum value
        :return: The int value
        :raise: WsBadRequestError
        """
        if value is None:
            raise WsBadRequestError(f'value for parameter "{name!r}" must be an integer list, but none was given')
        try:
            arr = list(map(int, value.split(',')))
            for value in arr:
                if minimum is not None and value < minimum:
                    raise WsBadRequestError(f'value of "{name!r}" list must not be < {minimum}, but was {value!r}')
                if maximum is not None and value > maximum:
                    raise WsBadRequestError(f'value of "{name!r}" list must not be > {maximum}, but was {value!r}')
            return arr
        except ValueError as e:
            raise WsBadRequestError(
                f'"value for parameter {name!r}" must be an integer list, but was {value!r}') from e

    @classmethod
    def to_float_list(cls,
                      name: str,
                      value: str,
                      minimum: float = None,
                      maximum: float = None) -> List[float]:
        """
        Convert str value to int array.
        :param name: Name of the value
        :param value: The string value
        :param minimum: Optional minimum value
        :param maximum: Optional maximum value
        :return: The int value
        :raise: WsBadRequestError
        """
        if value is None:
            raise WsBadRequestError(f'value for parameter "{name!r}" must be an number list, but none was given')
        try:
            arr = list(map(float, value.split(',')))
            for value in arr:
                if minimum is not None and value < minimum:
                    raise WsBadRequestError(f'value of "{name!r}" list must not be < {minimum}, but was {value!r}')
                if maximum is not None and value > maximum:
                    raise WsBadRequestError(f'value of "{name!r}" list must not be > {maximum}, but was {value!r}')
            return arr
        except ValueError as e:
            raise WsBadRequestError(
                f'"value for parameter {name!r}" must be an number list, but was {value!r}') from e

    @abstractmethod
    def get_query_argument(self, name: str, default: Optional[str]) -> Optional[str]:
        """
        Get query argument.
        :param name: Query argument name
        :param default: Default value.
        :return: the value or none
        :raise: WsBadRequestError
        """

    def get_query_argument_bool(self, name: str, default: int = None) -> Optional[bool]:
        """
        Get query argument of type int.
        :param name: Query argument name
        :param default: Default value.
        :return: boolean value
        :raise: WsBadRequestError
        """
        value = self.get_query_argument(name, default=None)
        return self.to_bool(name, value) if value else default

    def get_query_argument_int(self,
                               name: str,
                               default: int = None,
                               minimum: int = None,
                               maximum: int = None) -> Optional[int]:
        """
        Get query argument of type int.
        :param name: Query argument name
        :param default: Default value.
        :param minimum: Optional minimum value
        :param maximum: Optional maximum value
        :return: integer value
        :raise: WsBadRequestError
        """
        value = self.get_query_argument(name, default=None)
        return self.to_int(name, value, minimum=minimum, maximum=maximum) if value else default

    def get_query_argument_float(self,
                                 name: str,
                                 default: float = None,
                                 minimum: float = None,
                                 maximum: float = None) -> Optional[float]:
        """
        Get query argument of type float.
        :param name: Query argument name
        :param default: Default value.
        :param minimum: Optional minimum value
        :param maximum: Optional maximum value
        :return: float value
        :raise: WsBadRequestError
        """
        value = self.get_query_argument(name, default=None)
        return self.to_float(name, value, minimum=minimum, maximum=maximum) if value else default

    def get_query_argument_list(self,
                                name: str,
                                default: List[str] = None) -> Optional[List[str]]:
        """
        Get query argument of type float.
        :param name: Query argument name
        :param default: Default value.
        :return: string list value
        :raise: WsBadRequestError
        """
        value = self.get_query_argument(name, default=None)
        return self.to_list(name, value) if value else default

    def get_query_argument_int_list(self,
                                    name: str,
                                    default: List[int] = None,
                                    minimum: int = None,
                                    maximum: int = None) -> Optional[List[float]]:
        """
        Get query argument of type int.
        :param name: Query argument name
        :param default: Default value.
        :param minimum: Optional minimum value
        :param maximum: Optional maximum value
        :return: int list value
        :raise: WsBadRequestError
        """
        value = self.get_query_argument(name, default=None)
        return self.to_float_list(name, value, minimum=minimum, maximum=maximum) if value else default

    def get_query_argument_float_list(self,
                                      name: str,
                                      default: List[float] = None,
                                      minimum: float = None,
                                      maximum: float = None) -> Optional[List[float]]:
        """
        Get query argument of type float.
        :param name: Query argument name
        :param default: Default value.
        :param minimum: Optional minimum value
        :param maximum: Optional maximum value
        :return: float value
        :raise: WsBadRequestError
        """
        value = self.get_query_argument(name, default=None)
        return self.to_float_list(name, value, minimum=minimum, maximum=maximum) if value else default
