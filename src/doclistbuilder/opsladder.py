
"""A flexible options management system using a chain of responsibility pattern.

This module provides a metaclass-based system for managing hierarchical configuration options
in Python classes. The main components are:

- `OptionsLadder`: A metaclass that implements option inheritance through the class hierarchy


Example:
    ```python
    class MyOptions(OptionsBase):
        name: str "The name option."
        count: int "The count option."

    class Base(metaclass=OptionsLadder):
        _defaults = {"name": "default", "count": 42}
    ```
"""

from typing import TypedDict, Any
from collections import ChainMap


class OptionsLadder(type):
    """Metaclass for classes with options."""

    class HasOptions():  # pylint: disable=too-few-public-methods
        """Marker for classes with options."""

    settings: ChainMap[str, Any]

    def __new__(
        mcs,
        cname: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any]
    ):
        n_cls = super().__new__(mcs, cname, bases, namespace)

        d: ChainMap[str, Any] = ChainMap()
        for c in reversed(n_cls.mro()):
            if issubclass(c, OptionsLadder.HasOptions) and hasattr(c, '_defaults'):
                d = ChainMap(getattr(c, "_defaults"), d)

        n_cls.settings = d

        return n_cls


class OptionsBase(TypedDict):
    """Empty base class for options tracking."""


def options_filter(
    x: OptionsBase,
    s: object
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Filter options based on the type annotations of the given class."""
    return (
        {k: v for k, v in x.items() if k in s.__annotations__},
        {k: v for k, v in x.items() if k not in s.__annotations__},
    )
