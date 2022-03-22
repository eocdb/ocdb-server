import pprint
from datetime import datetime
from typing import Any, Dict, Type, TypeVar

T = TypeVar('T')


class Model(object):
    """
    Base class for all models.
    """

    @classmethod
    def from_dict(cls: Type[T], dictionary: Dict[str, Any]) -> T:
        """Get the dictionary ``d`` as a model."""
        if dictionary is None:
            return None
        obj = cls.__new__(cls)
        for name, value in dictionary.items():
            if not hasattr(cls, name):
                raise ValueError(f'property "{name}" is not an attribute of {cls}')
            prop = getattr(cls, name)
            if not isinstance(prop, property):
                raise ValueError(f'property "{name}" is not a property of {cls}')
            return_type = None
            if prop.fget and hasattr(prop.fget, "__annotations__"):
                annotations = prop.fget.__annotations__
                if annotations and "return" in annotations:
                    return_type = annotations["return"]
            if return_type in {None, str, int, float, bool, complex, list}:
                setattr(obj, name, value)
            elif hasattr(return_type, "__name__") \
                    and hasattr(return_type, "__args__") \
                    and return_type.__name__ == 'List':
                item_type = return_type.__args__[0]
                if hasattr(item_type, "from_dict"):
                    new_list = []
                    for item in value:
                        item_obj = item_type.from_dict(item)
                        new_list.append(item_obj)
                    setattr(obj, name, new_list)
                else:
                    setattr(obj, name, value)
            elif return_type is not None and hasattr(return_type, "from_dict"):
                obj_value = return_type.from_dict(value)
                setattr(obj, name, obj_value)
            else:
                setattr(obj, name, value)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        """Get the model properties as a dict."""
        result = {}

        prop_names = [k[1:] for k in self.__dict__ if hasattr(self, k) and k.startswith('_')]
        for prop_name in prop_names:
            value = getattr(self, prop_name)
            if isinstance(value, list):
                result[prop_name] = list(map(self._to_dict, value))
            elif hasattr(value, "to_dict"):
                result[prop_name] = value.to_dict()
            elif isinstance(value, dict):
                result[prop_name] = dict(map(self._to_dict_pair, value.items()))
            elif isinstance(value, datetime):
                result[prop_name] = str(value)
            else:
                result[prop_name] = value

        return result

    @classmethod
    def _to_dict(cls, x):
        if isinstance(x, datetime):
            return str(x)

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
        return not (self == other)
