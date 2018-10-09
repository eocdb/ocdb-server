from typing import Optional, Any, Set


def assert_cond(cond: bool, message: str):
    if not cond:
        raise ValueError(message)


def assert_not_empty(value: str, name: str):
    if value == '':
        raise ValueError(f'{name} must not be empty')


def assert_not_none(value: Any, name: str):
    if value is None:
        raise ValueError(f'{name} must not be None')


def assert_not_none_not_empty(value: Optional[str], name: str):
    assert_not_none(value, name)
    assert_not_empty(value, name)


def assert_one_of(value: Optional[Any], name: str, enum: Set[Any]):
    if value not in enum:
        raise ValueError(f'{name} must be one of {enum}, was {repr(value)}')
