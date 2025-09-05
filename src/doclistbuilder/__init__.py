r"""
Helper functions for building LaTeX documents.
LaTeX uses a mix of sequential and nested structures. The document
as a whole is a sequence of command with the body of the document
nested inside a document environment. Environments, for example,
are defined using \being{name} ... \end{name} structure. These
helper classes assume this structure, that is, they build a list
of things that can then be assembled by concatenation (maybe with
a deliminator) into something that nested as an item in a higher
level list.

The classes are intended to be used as context managers. The target
context variable is an extension of list. On closing the context
it will assemble and append to the parent context variable (if any).
"""

from .opsladder import OptionsLadder, OptionsBase, options_filter
from .assemblable import Assemblable, AssembleList
from .llatex import DocumentPart, NewCommand, Environment, LatexList

__all__ = [
    "OptionsLadder", "OptionsBase", "options_filter",
    "Assemblable", "AssembleList",
    "DocumentPart", "NewCommand", "Environment", "LatexList",
]
