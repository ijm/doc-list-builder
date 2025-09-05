"""A flexible framework for building and transforming lists through context managers.

This module provides the `Assemblable` base class and `AssembleList` container that together
enable a clean, context-manager based approach to building and transforming lists. The main
features include:

- Chainable context managers for building nested list structures
- Pipeline processing of list contents

Example:
    ```python
    alist = Assemblable()
    with alist as items:
        items.extend(['a', 'b', 'c'])
        with Assemblable(items) as more_items:
            more_items.extend(['d', 'e'])
    print(alist.result)  # ['a', 'b', 'c', 'd', 'e']
    ```

When the context manager is closed, the pipeline is run over the list, and the result is
appended to the parent list.
"""

from types import TracebackType
from typing import (Self, Type, Callable, NotRequired, Unpack, Any)
from collections import ChainMap

from .opsladder import OptionsLadder, OptionsBase


class AssembleList(list[str]):
    """A wrapper class for a list with some additional functions."""
    def __init__(
        self: Self,
        init: list[str] | None = None,
        context: 'Assemblable | None' = None,
    ) -> None:
        super().__init__(init or [])
        self._context: 'Assemblable | None' = context

    def __repr__(self) -> str:
        return f"AssembleList({list(self)!r})"

    @property
    def context(self: Self) -> 'Assemblable | None':
        """Return the context manager."""
        return self._context


class Assemblable(OptionsLadder.HasOptions, metaclass=OptionsLadder):
    """Base class for assemblable objects."""
    class Options(OptionsBase):
        """Options for assemblable objects."""
        list_type: NotRequired[Type[AssembleList]]
        "The type of assemblable list to use."

        pipeline: NotRequired[list[Callable[[list[str]], list[str]]]]
        """
        The pipeline of functions to fold over the list when the context
        is closed.
        """

        initial_list: NotRequired[list[str]]
        "Initialize the assemblable list with this list."

    _defaults: Options = {  # type: ignore[assignment]
        "list_type": AssembleList,
        "initial_list": [],
        "pipeline": [],
    }

    settings: ChainMap[str, Any]

    def __init__(
        self,
        parent: AssembleList | None = None,
        **kwargs: Unpack[Options]
    ) -> None:

        self.settings = ChainMap({}, self.settings)
        self.settings.update(kwargs.items())  # Drop typing.

        self._result: list[str] | None = None
        self._parent = parent
        self.data = self.settings['list_type'](
            self.settings['initial_list'], self
        )

    def __enter__(self: Self):
        return self.data

    def __exit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> None:
        self._result = self.run_pipeline(self.data)

        if self._parent is not None:
            self._parent.extend(self._result)

        return None

    def run_pipeline(self: Self, data: list[str]) -> list[str]:
        """Run the pipeline of functions over the list."""
        for func in self.settings['pipeline']:
            data = func(data)
        return data

    @property
    def result(self: Self) -> list[str] | None:
        """Return the result of the pipeline."""
        if self._result is None:
            raise ValueError(
                "Assemblable context manager has not been closed."
            )

        return self._result

    @property
    def parent(self: Self) -> AssembleList | None:
        """Return the parent context manager."""
        return self._parent
