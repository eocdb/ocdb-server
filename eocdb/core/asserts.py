from typing import Any, Sequence, Set, Collection


def assert_not_empty(value: Any, name: str):
    is_empty = False
    if isinstance(value, (str, list, dict, set)):
        is_empty = not value
    if is_empty:
        raise ValueError(f'{name} must not be empty')


def assert_not_none(value: Any, name: str):
    if value is None:
        raise ValueError(f'{name} must not be None')


def assert_not_none_not_empty(value: Any, name: str):
    assert_not_none(value, name)
    assert_not_empty(value, name)


def assert_one_of(value: Any, name: str, enum: Collection[Any]):
    if value not in enum:
        raise ValueError(f'{name} must be one of {repr(enum)}, but was {repr(value)}')
