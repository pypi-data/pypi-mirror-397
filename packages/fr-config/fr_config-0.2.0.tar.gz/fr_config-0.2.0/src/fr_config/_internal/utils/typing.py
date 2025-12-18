# Copyright (C) 2024 Floating Rock Studio Ltd
# File copied from fr_common.sequence
from typing import Sequence, Set, Generator, Iterator, List

_SEQUENCE_TYPES = (Sequence, Set, Generator, Iterator)


def ensure_list(value):
    """Given a value, ensure it is a list

    Args:
        value(value)

    Returns:
        List
    """
    if isinstance(value, (str, bytes)):
        return [value]

    if isinstance(value, List):
        return value

    if isinstance(value, _SEQUENCE_TYPES):
        return list(value)
    if value is None:
        return []
    return [value]


def flatten(value):
    """Given a nested list of lists, flatten to a single list as a generator

    Args:
        value(value)

    Yields:
        List
    """
    for each in ensure_list(value):
        if isinstance(each, (str, bytes)):
            yield value
        elif isinstance(each, _SEQUENCE_TYPES):
            yield from flatten(each)
        else:
            yield each


def first_index(value, default=None):
    """Return the first index of the value in a safe way

    Args:
        value(value)
        default(value): value to return if list is empty

    Returns:
        value
    """
    if value is None:
        return default
    values = ensure_list(value)
    if values:
        return values[0]
    return default


def last_index(value, default=None):
    """Return the first index of the value in a safe way

    Args:
        value(value)
        default(value): value to return if list is empty

    Returns:
        value
    """
    if value is None:
        return default
    values = ensure_list(value)
    if values:
        return values[-1]
    return default


# Aliases for convenience
fi = first_index
li = last_index
