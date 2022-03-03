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
from datetime import datetime
from typing import Optional, List, Union

from .errors import WsBadRequestError
from ..core import UNDEFINED


class RequestParams(metaclass=ABCMeta):
    @classmethod
    def to_bool(cls, name: str, value: str) -> Union[bool, None]:
        """
        Convert str value to int.
        :param name: Name of the value
        :param value: The string value
        :return: The int value
        :raise: WsBadRequestError
        """
        if value is None or value is UNDEFINED:
            raise cls._error_missing(name)
        try:
            value = value.lower()
            if value == 'true':
                return True
            if value == 'false':
                return False
            return bool(int(value))
        except ValueError as e:
            raise cls._error_wrong_type(name, "boolean") from e

    @classmethod
    def to_date(cls, name: str, value: str, raises: bool = True) -> Union[datetime, str]:
        """
        Convert str value to int.
        :param name: Name of the value
        :param value: The string value
        :param raises: If true thei method will raise an error otherwise return the value unchanged
        :return: The datetime value
        :raise: WsBadRequestError
        """
        if value is None or value is UNDEFINED:
            raise cls._error_missing(name)
        try:
            return datetime.strptime(value, '%Y-%m-%dT%H:%M')
        except ValueError as e:
            if not raises:
                return value
            raise cls._error_wrong_type(name, "datetime") from e

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
        if value is None or value is UNDEFINED:
            raise cls._error_missing(name)
        try:
            value = int(value)
            cls._check_min_max(name, value, maximum, minimum)
            return value
        except ValueError as e:
            raise cls._error_wrong_type(name, "integer") from e

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
        if value is None or value is UNDEFINED:
            raise cls._error_missing(name)
        try:
            value = float(value)
            cls._check_min_max(name, value, maximum, minimum)
            return value
        except ValueError as e:
            raise cls._error_wrong_type(name, "number") from e

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
            raise cls._error_missing(name)
        return value

    @classmethod
    def to_int_list(cls,
                    name: str,
                    value: Union[str, List[str]],
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
        if value is None or value is UNDEFINED:
            raise cls._error_missing(name)
        try:
            if isinstance(value, list):
                arr = list(map(int, value))
            else:
                arr = list(map(int, value.split(',')))
            cls._check_list_min_max(name, arr, maximum, minimum)
            return arr
        except ValueError as e:
            raise cls._error_wrong_type(name, "list of integer") from e

    @classmethod
    def to_float_list(cls,
                      name: str,
                      value: Union[str, List[str]],
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
        if value is None or value is UNDEFINED:
            raise cls._error_missing(name)
        try:
            if isinstance(value, list):
                arr = list(map(float, value))
            else:
                arr = list(map(float, value.split(',')))
            cls._check_list_min_max(name, arr, maximum, minimum)
            return arr
        except ValueError as e:
            raise cls._error_wrong_type(name, "list of numbers") from e

    @abstractmethod
    def get_param(self, name: str, default: Optional[str] = UNDEFINED) -> Optional[str]:
        """
        Get query argument.
        :param name: Query argument name
        :param default: Default value.
        :return: the value or none
        :raise: WsBadRequestError
        """

    @abstractmethod
    def get_params(self, name: str) -> Optional[str]:
        """
        Get query argument array.
        :param name: Query argument name
        :return: the values or an empyty array
        :raise: WsBadRequestError
        """

    def get_param_bool(self, name: str, default: int = None) -> Optional[bool]:
        """
        Get query argument of type int.
        :param name: Query argument name
        :param default: Default value.
        :return: boolean value
        :raise: WsBadRequestError
        """
        value = self.get_param(name, default=None)
        return self.to_bool(name, value) if value else default

    def get_param_int(self,
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
        value = self.get_param(name, default=None)
        return self.to_int(name, value, minimum=minimum, maximum=maximum) if value else default

    def get_param_float(self,
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
        value = self.get_param(name, default=None)
        return self.to_float(name, value, minimum=minimum, maximum=maximum) if value else default

    def get_param_list(self,
                       name: str,
                       default: List[str] = None) -> Optional[List[str]]:
        """
        Get query argument of type float.
        :param name: Query argument name
        :param default: Default value.
        :return: string list value
        :raise: WsBadRequestError
        """
        value = self.get_params(name)
        if isinstance(value, str):
            return self.to_list(name, value) if value else default
        elif value is None or len(value) == 0:
            return default
        else:
            return value

    def get_param_int_list(self,
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
        value = self.get_param(name, default=None)
        if isinstance(value, str) or isinstance(value, list):
            return self.to_float_list(name, value, minimum=minimum, maximum=maximum) if value else default
        elif value is None or len(value) == 0:
            return default
        else:
            return value

    def get_param_float_list(self,
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
        value = self.get_params(name)
        if isinstance(value, str) or isinstance(value, list):
            return self.to_float_list(name, value, minimum=minimum, maximum=maximum) if value else default
        elif value is None or len(value) == 0:
            return default
        else:
            return value

    @classmethod
    def _check_min_max(cls, name, value, maximum, minimum):
        if minimum is not None and value < minimum:
            raise cls._error_too_small(name, minimum)
        if maximum is not None and value > maximum:
            raise cls._error_too_large(name, maximum)

    @classmethod
    def _check_list_min_max(cls, name, value, maximum, minimum):
        for value in value:
            cls._check_min_max(name, value, maximum, minimum)

    @classmethod
    def _error_missing(cls, param_name):
        return WsBadRequestError(f"Missing value for parameter '{param_name}'")

    @classmethod
    def _error_wrong_type(cls, param_name, type_name):
        return WsBadRequestError(f"Value for parameter '{param_name}' must be a {type_name}")

    @classmethod
    def _error_too_small(cls, param_name, minimum):
        return WsBadRequestError(f"Value of parameter '{param_name}' must not be < {minimum}")

    @classmethod
    def _error_too_large(cls, param_name, maximum):
        return WsBadRequestError(f"Value of parameter '{param_name}' must not be > {maximum}")
