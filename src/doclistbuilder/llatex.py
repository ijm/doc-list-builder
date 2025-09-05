
"""A LaTeX document builder with a clean, Pythonic API.

This module provides tools for programmatically generating LaTeX documents with proper escaping
and structure. It builds on the `Assemblable` framework to provide LaTeX-specific functionality.

Main components:
- `LatexList`: Enhanced list with LaTeX-specific helpers
- `DocumentPart`: Base class for LaTeX document components
- `NewCommand`: For defining LaTeX commands
- `Environment`: For creating LaTeX environments

Example:
    ```python
    doc = DocumentPart()

    with Environment(doc, 'document') as doc:
        with NewCommand(doc, 'mycommand') as cmd:
            cmd.append('\\textbf{Hello, #1!}')
        doc.append('\\mycommand{World}')

    print(doc.result)  # Outputs the complete LaTeX document
    ```
"""

from typing import Self, NotRequired, Unpack
import re
from collections import ChainMap

from .assemblable import AssembleList, Assemblable
from .opsladder import options_filter


class LatexList(AssembleList):
    """Helper functions for LaTeX document lists."""

    def desc_item(self: Self, key: str, value: str) -> None:
        """Append a description-like item."""
        self.append(f"\\item [{{{key}}}] {value}")

    def rule(
        self: Self,
        width: str = r"\textwidth",
        height: str = "0.4pt"
    ) -> None:
        """Append a horizontal rule."""
        self.append(rf"\rule{{{width}}}{{{height}}}")


class DocumentPart(Assemblable):
    """Base class for document parts."""
    class Options(Assemblable.Options):
        """Options for document parts."""
        name: NotRequired[str | None]
        "Optional name of the Document Part (e.g. command or environment name)."

        prolog: NotRequired[str]
        "Optional prefix string to add to the list."

        epilog: NotRequired[str]
        "Optional The suffix string to add to the list."

        delimiter: NotRequired[str]
        "The delimiter string to join the list with."

    _defaults: Options = {  # type: ignore[assignment]
        "list_type": LatexList,
        "name": None,
        "prolog": "",
        "epilog": "",
        "delimiter": "\n"
    }

    def __init__(
        self,
        parent: AssembleList | None = None,
        **kwargs: Unpack[Options]
    ) -> None:
        """Initialize a new DocumentPart context manager."""

        self._defaults['pipeline'] = [self.p_join, self.p_wrap]

        (up, down) = options_filter(kwargs, super().Options)
        self.settings = ChainMap(down, self.settings)
        super().__init__(parent, **up)

    @property
    def name(self: Self) -> str | None:
        """Return the name of the document part if it is set."""
        return self.settings['name']

    def p_join(self: Self, data: list[str]) -> list[str]:
        """Join a list with the set delimiter."""
        return [self.settings['delimiter'].join(data)]

    def p_wrap(self: Self, data: list[str]) -> list[str]:
        """Wrap a list with the set prefix and suffix."""
        return (["".join([self.settings['prolog']] + data + [self.settings['epilog']])])


def validate_latex_control_word(name: str) -> None:
    """Validate that a string is a valid LaTeX command name.

    LaTeX command names must start with a backslash and a letter,
    and can contain only letters. Special characters like @, *, and
    : are allowed in some contexts.

    Raises:
        ValueError: If the name is not a valid LaTeX command name
    """

    if not name:
        raise ValueError("Command name cannot be empty")

    if not re.fullmatch(r'[a-zA-Z][a-zA-Z@*:]*', name):
        raise ValueError(
            f"Invalid command name: {name!r}. Must start with a letter and "
            "contain only letters, @, *, or :"
        )


def validate_environment_name(name: str) -> None:
    """Validate that a string is a valid LaTeX environment name.

    LaTeX environment names must start with a letter and can contain
    letters, numbers, @, and *.

    Raises:
        ValueError: If the name is not a valid LaTeX environment name
    """
    if not name:
        raise ValueError("Environment name cannot be empty")

    if not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9@*]*', name):
        raise ValueError(
            f"Invalid environment name: {name!r}. Must start with a letter "
            "and contain only letters, numbers, @, or *"
        )


class NewCommand(DocumentPart):
    r"NewCommand like document components of the form \newcommand{name}{...}."

    class Options(DocumentPart.Options):
        """Available options for NewCommand."""
        nargs: NotRequired[int]
        "The number of arguments (default: 0)"

        default: NotRequired[str | None]
        "The default arguments (default: None)"

    _defaults: Options = {  # type: ignore[assignment]
        "nargs": 0,
        "default": None,
        "epilog": "\n}%",
        "delimiter": "\n",
    }

    def __init__(
        self: Self,
        parent: AssembleList | None,
        cmd_name: str,
        **kwargs: Unpack[Options]
    ) -> None:

        kwargs['name'] = cmd_name
        self.validate_and_update(**(self._defaults | kwargs))

        (up, down) = options_filter(kwargs, super().Options)
        self.settings = ChainMap(down, self.settings)
        super().__init__(parent, **up)

    def validate_and_update(self, *, name, nargs, default, **_) -> None:
        """
        Validate and update the default settings, for this
        NewCommand context manager.
        """

        validate_latex_control_word(name)

        if nargs < 0 or nargs > 9:
            raise ValueError(f"nargs must be between 0 and 9, got {nargs}")

        self._defaults['prolog'] = (
            f"\\newcommand{{\\{name}}}"
            + (f"[{nargs}]" if nargs > 0 else "")
            + (f"[{default}]" if default is not None else "")
            + "{%\n"
        )


class Environment(DocumentPart):
    r"Environment like document components of the form \begin{name} ... \end{name}."
    class Options(DocumentPart.Options):
        """Available options for Environment."""
        args: NotRequired[str | None]
        "The arguments (in {}) to the environment (default: None)"

        ops: NotRequired[str | None]
        "The options (in []) to the environment (default: None)"

    _defaults: Options = {  # type: ignore[assignment]
        "args": None,
        "ops": None,
        "delimiter": "\n",
    }

    def __init__(
        self: Self,
        parent: AssembleList | None,
        env_name: str,
        **kwargs: Unpack[Options]
    ) -> None:

        kwargs['name'] = env_name

        self.validate_and_update(**(self._defaults | kwargs))

        (up, down) = options_filter(kwargs, super().Options)
        self.settings = ChainMap(down, self.settings)
        super().__init__(parent, **up)

    def validate_and_update(self, *, name, args, ops, **_) -> None:
        """
        Validate and update the default settings, for this Environment
        context manager.
        """
        validate_environment_name(name)
        self._defaults['prolog'] = (
            rf"\begin{{{name}}}"
            + (f"[{ops}]" if ops else "")
            + (f"{{{args}}}" if args else "")
            + "%\n"
        )
        self._defaults['epilog'] = f"\n\\end{{{name}}}%"
