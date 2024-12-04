"""Unit tests to examine the Expected Behavior of the EpiLog Logging Manager."""

import logging
import os
from io import StringIO

import pytest

from EpiLog import EpiLog
from EpiLog.manager import defaultFormat


@pytest.mark.parametrize("names", [("a", "b", "c"), ("b", "c", "d", "e")])
def test_get_logger(names, build_manager) -> None:
    """Tests that we correctly construct a named logger."""
    manager: EpiLog = build_manager()
    assert len(manager.loggers) == 0

    for n in names:
        manager.get_logger(n)
    assert len(manager.loggers) == len(names)
    assert all(i in manager.loggers for i in names)


def test_logging(build_manager) -> None:
    """Makes certain no errors are raised while logging."""
    manager: EpiLog = build_manager()
    log = manager.get_logger("test")
    log.info("Bob boop beep")


def test_stream(build_manager) -> None:
    """Tests that the message output by logging is actually written to stream."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    manager: EpiLog = build_manager(stream=handler)

    log = manager.get_logger("test")
    message = "You are blind to reality and for that I am most proud"
    log.info(message)

    stream.seek(0)
    output = stream.read()
    stream.close()

    assert message in output, "Message not Found in output stream after logging"


def test_level_change(build_manager) -> None:
    """Tests that modifying the Logging Level accurately filters log output."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)

    manager: EpiLog = build_manager(level=logging.INFO, stream=handler)
    log: logging.Logger = manager.get_logger("test")

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


def test_format_change(build_manager) -> None:
    """Tests that modifying the Logging Format accurately Modifies log output Format."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    manager: EpiLog = build_manager(level=logging.INFO, stream=handler)
    log: logging.Logger = manager.get_logger("test")

    # Modify Formatter
    manager.formatter = logging.Formatter("%(levelname)s | %(message)s")
    message = "I have no idea why all of this is happening or how to control it."
    log.info(message)

    stream.seek(0)
    output = stream.read()
    stream.close()

    assert f"INFO | {message}\n" == output, "Expected Message format to match."


def test_stream_change(build_manager) -> None:
    """Tests that modifying the Logging Stream writes to the correct Stream."""
    stream_a = StringIO()
    stream_b = StringIO()
    handler_a = logging.StreamHandler(stream_a)
    handler_b = logging.StreamHandler(stream_b)

    manager: EpiLog = build_manager(
        level=logging.INFO,
        stream=handler_a,
        formatter=logging.Formatter("%(levelname)s | %(message)s"),
    )
    log = manager.get_logger("test")

    # Modify Stream
    manager.stream = handler_b
    assert manager.stream == handler_b, "Unexpected Stream."

    message = (
        "You humans have so many emotions! You only need two: anger and confusion!"
    )
    expected = f"INFO | {message}\n"
    log.info(message)

    # Test first stream
    stream_a.seek(0)
    output_a = stream_a.read()
    stream_a.close()
    assert (
        output_a != expected
    ), "Did not Expect message to be written to previous stream."

    # Test Second, Expected stream
    stream_b.seek(0)
    output_b = stream_b.read()
    stream_b.close()
    assert output_b == expected, "Expected message to be written to current stream."


def test_stream_change_to_none(build_manager) -> None:
    """Confirm that attempts to set the stream to none result in default stream."""
    manager: EpiLog = build_manager()
    assert manager.stream is not None, "Expected Default Stream to instantiate."
    previous_id = id(manager.stream)

    manager.stream = None  # type: ignore[assignment]
    assert manager.stream is not None, "Expected Default Stream to kick in."
    assert isinstance(
        manager.stream, (logging.Handler, logging.Filterer)
    ), "Unexpected stream type."

    assert id(manager.stream) != previous_id, "Expected new stream instance."


@pytest.mark.parametrize(
    "f",
    [
        None,
        logging.Formatter("%(name)s | %(levelname)s | %(message)s"),
    ],
)
def test_format(f, build_manager) -> None:
    """Tests expected behaviors when instantiating with Formatters."""
    manager: EpiLog = build_manager(formatter=f)
    if f is not None:
        assert manager.formatter == f, "Expected Logging Format to reflect input."
    else:
        assert id(manager.formatter) == id(defaultFormat), "Expected default formatter"


def test_format_error(build_manager) -> None:
    """Test TypeError is raised when instantiating with invalid Formatters."""
    with pytest.raises(TypeError):
        build_manager(formatter="Failure")


@pytest.mark.parametrize(
    "level",
    [
        logging.NOTSET,
        logging.DEBUG,
        logging.INFO,
        logging.WARN,
        logging.ERROR,
        logging.CRITICAL,
    ],
)
def test_levels(level, build_manager) -> None:
    """Tests Expected instantiation Behavior of EpiLog class with Logging Level."""
    manager: EpiLog = build_manager(level=level)
    assert manager.level == level, "Expected Logging Level to be reflect input."


def test_level_error(build_manager) -> None:
    """Tests ValueError is raised Expected when instantiating invalid Logging Level."""
    with pytest.raises(ValueError):
        build_manager(level=-1)


@pytest.mark.parametrize(
    "handler",
    [
        logging.FileHandler("test.log"),
        logging.StreamHandler(),
    ],
)
def test_handlers(handler, build_manager) -> None:
    """Tests Expected instantiation Behavior of EpiLog class with stream."""
    manager: EpiLog = build_manager(stream=handler)

    # Cleanup by removing file created by file handler
    if isinstance(handler, logging.FileHandler):
        os.remove(handler.baseFilename)

    assert manager.stream == handler, "Expected Stream to reflect input."


def test_handlers_error(build_manager) -> None:
    """Tests TypeError is raised Expected when instantiating invalid stream."""
    with pytest.raises(TypeError):
        build_manager(stream="handler")


def test_get_log_by_name(build_manager) -> None:
    """Tests the special dunder method __get_item__ works as expected."""
    manager: EpiLog = build_manager()
    name = "get_item"
    log: logging.Logger = manager.get_logger(name)

    assert manager[name] == log, "Expected to retrieve the same logger via get item."
