"""Pytest configuration and fixtures for doclistbuilder tests."""
import pytest
from typing import Generator

from doclistbuilder.assemblable import AssembleList, Assemblable


@pytest.fixture
def empty_list() -> AssembleList:
    """Return an empty AssembleList."""
    return AssembleList()


@pytest.fixture
def sample_list() -> AssembleList:
    """Return an AssembleList with sample data."""
    return AssembleList(["item1", "item2", "item3"])


@pytest.fixture
def sample_assemblable() -> Generator[Assemblable, None, None]:
    """Return a basic Assemblable instance for testing."""
    with Assemblable() as a:
        yield a
