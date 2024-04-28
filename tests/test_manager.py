"""Unit tests to examine the Expected Behavior of the EpiLog Logging Manager."""

import logging
import os
from io import StringIO

import pytest

from EpiLog.manager import EpiLog


@pytest.mark.parametrize("names", [("a", "b", "c"), ("b", "c", "d", "e")])
def test_get_logger(names):
    """Tests that we correctly construct a named logger."""
    manager = EpiLog()
    assert len(manager.loggers) == 0

    for n in names:
        manager.get_logger(n)
    assert len(manager.loggers) == len(names)
    assert all(i in manager.loggers for i in names)


def test_logging():
    """Makes certain no errors are raised while logging."""
    manager = EpiLog()
    log = manager.get_logger("test")
    log.info("Bob boop beep")


def test_stream():
    """Tests that the message output by logging is actually written to stream."""
    stream = StringIO()

    handler = logging.StreamHandler(stream)
    manager = EpiLog(stream=handler)
    log = manager.get_logger("test")
    message = "You are blind to reality and for that I am most proud"
    log.info(message)

    stream.seek(0)
    output = stream.read()
    stream.close()

    assert message in output, "Message not Found in output stream after logging"


def test_level_change():
    """Tests that modifying the Logging Level accurately filters log output."""
    stream = StringIO()

    handler = logging.StreamHandler(stream)
    manager = EpiLog(level=logging.INFO, stream=handler)
    log = manager.get_logger("test")

    message = (
        "I would say that he's blessedly unburdened with the complications of a"
        " university education."
    )
    log.debug(message)
    stream.seek(0)
    output = stream.read()
    assert message not in output, "Message should not have been Received"

    # Then repeat after Changing level
    manager.level = logging.DEBUG
    log.debug(message)

    stream.seek(0)
    output = stream.read()
    stream.close()

    assert message in output, "Message not Found in output stream after logging"


def test_format_change():
    """Tests that modifying the Logging Format accurately Modifies log output Format."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    manager = EpiLog(level=logging.INFO, stream=handler)
    log = manager.get_logger("test")

    # Modify Formatter
    manager.formatter = logging.Formatter("%(levelname)s | %(message)s")
    message = "I have no idea why all of this is happening or how to control it."
    log.info(message)

    stream.seek(0)
    output = stream.read()
    stream.close()

    assert f"INFO | {message}\n" == output


def test_stream_change():
    """Tests that modifying the Logging Stream writes to the correct Stream."""
    stream_a = StringIO()
    stream_b = StringIO()
    handler_a = logging.StreamHandler(stream_a)
    handler_b = logging.StreamHandler(stream_b)

    manager = EpiLog(
        level=logging.INFO,
        stream=handler_a,
        formatter=logging.Formatter("%(levelname)s | %(message)s"),
    )
    log = manager.get_logger("test")

    # Modify Stream
    manager.stream = handler_b
    assert manager.stream == handler_b

    message = (
        "You humans have so many emotions! You only need two: anger and confusion!"
    )
    expected = f"INFO | {message}\n"
    log.info(message)

    # Test first stream
    stream_a.seek(0)
    output_a = stream_a.read()
    stream_a.close()
    assert output_a != expected

    # Test Second, Expected stream
    stream_b.seek(0)
    output_b = stream_b.read()
    stream_b.close()
    assert output_b == expected


@pytest.mark.parametrize(
    "f",
    [
        None,
        pytest.param("Failure", marks=pytest.mark.xfail(raises=TypeError)),
        logging.Formatter("%(name)s | %(levelname)s | %(message)s"),
    ],
)
def test_format(f):
    """Tests expected behaviors when instantiating with Formatters."""
    manager = EpiLog(formatter=f)
    manager.formatter = f


@pytest.mark.parametrize(
    "level",
    [
        logging.NOTSET,
        logging.DEBUG,
        logging.INFO,
        logging.WARN,
        logging.ERROR,
        logging.CRITICAL,
        pytest.param(-1, marks=pytest.mark.xfail(raises=ValueError)),
    ],
)
def test_levels(level):
    """Tests Expected instantiation Behavior of EpiLog class with Logging Level."""
    manager = EpiLog(level=level)
    assert manager.level == level


@pytest.mark.parametrize(
    "handler",
    [
        logging.FileHandler("test.log"),
        logging.StreamHandler(),
        pytest.param("handler", marks=pytest.mark.xfail(raises=TypeError)),
    ],
)
def test_handlers(handler):
    """Tests Expected instantiation Behavior of EpiLog class with stream."""
    manager = EpiLog(stream=handler)

    # Cleanup by removing file created by file handler
    if isinstance(handler, logging.FileHandler):
        os.remove(handler.baseFilename)

    assert manager.stream == handler
