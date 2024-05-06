"""Pytest Fixtures and Utilities."""

import logging
from typing import Callable, Generator, Optional

import pytest

from EpiLog.manager import EpiLog


def teardown_logs(epilog: EpiLog) -> None:
    """Handle Teardown of EpiLog Manager."""
    names = epilog.loggers.keys()
    epilog.loggers.clear()

    # Remove names from Global Logging Root
    for key in names:
        logging.Logger.manager.loggerDict.pop(key)


@pytest.fixture
def build_manager() -> Generator[Callable[..., EpiLog], None, None]:
    """Construct an EpiLog Instance and Handles Tear down of creating new Loggers."""
    instance: Optional[EpiLog] = None

    def builder(*args, **kwargs) -> EpiLog:
        nonlocal instance
        instance = EpiLog(*args, **kwargs)
        return instance

    yield builder

    # Required for Intentionally Failed Tests
    if instance is not None:
        teardown_logs(instance)
