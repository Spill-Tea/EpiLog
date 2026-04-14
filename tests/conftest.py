"""Pytest Fixtures and Utilities."""

from __future__ import annotations

import logging
import os
from io import IOBase
from typing import Callable, Generator, Optional

import pytest

from EpiLog.manager import EpiLog


def teardown_handler(handler: logging.Handler):
    """Teardown a single handler."""
    if not handler.stream.closed:
        handler.flush()
        handler.close()

    if isinstance(handler, logging.FileHandler):
        filename = handler.baseFilename
        os.remove(filename)
        assert not os.path.exists(filename), "Expected to Remove Logging Filepath."


def teardown_logger_handlers(log: logging.Logger):
    """Close and remove open streams from handlers connected to a logger instance."""
    log.propagate = False
    for handler in log.handlers:
        teardown_handler(handler)
    log.handlers.clear()


def teardown_epilogs(epilog: EpiLog) -> None:
    """Handle Teardown of EpiLog Manager."""
    for key, logger in epilog.loggers.items():
        logging.Logger.manager.loggerDict.pop(key)
        teardown_logger_handlers(logger)
    epilog.loggers.clear()
    teardown_handler(epilog.stream)


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
        teardown_epilogs(instance)


def _assert_msg_in_output(stream: IOBase, msg: str) -> None:
    stream.seek(0)
    output: str = stream.read()
    assert msg in output, "Message not found in output stream after logging."
