
import pprint
from typing import Any, Dict, Type, TypeVar

T = TypeVar('T')


class Model(object):

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> T:
        """Get the dictionary ``d`` as a model."""
        # TODO deserialize model
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        """Get the model properties as a dict."""
        result = {}

        prop_names = [k for k in self.__dict__ if hasattr(self, k) and hasattr(self, "_" + k)]
        for prop_name in prop_names:
            value = getattr(self, prop_name)
            if isinstance(value, list):
                result[prop_name] = list(map(self._to_dict, value))
            elif hasattr(value, "to_dict"):
                result[prop_name] = value.to_dict()
            elif isinstance(value, dict):
                result[prop_name] = dict(map(self._to_dict_pair, value.items()))
            else:
                result[prop_name] = value

        return result

    @classmethod
    def _to_dict(cls, x):
        return x.to_dict() if hasattr(x, "to_dict") else x

    @classmethod
    def _to_dict_pair(cls, x):
        key, value = x
        if not hasattr(value, "to_dict"):
            return x
        return key, value.to_dict()

    def to_str(self) -> str:
        """Returns the string representation of the model

        :rtype: str
        """
        return pprint.pformat(self.to_dict())

    def __repr__(self) -> str:
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other) -> bool:
        """Returns true if both objects are equal"""
        return self.__dict__ == other.__dict__

    def __ne__(self, other) -> bool:
        """Returns true if both objects are not equal"""
        return not self == other

