"""Unit tests to examine the Expected Behavior of the EpiLog Logging Manager."""

from __future__ import annotations

import logging
import sys
from io import IOBase, StringIO
from typing import Callable, Tuple, Union

import pytest

from EpiLog import EpiLog
from EpiLog.manager import defaultFormat


@pytest.mark.parametrize("names", [("a", "b", "c"), ("b", "c", "d", "e")])
@pytest.mark.parametrize("fn_name", ["get_logger", "dispatch"])
def test_get_logger(
    names: Tuple[str],
    fn_name: str,
    build_manager: Callable[..., EpiLog],
) -> None:
    """Tests that we correctly construct a named logger."""
    manager: EpiLog = build_manager()
    assert len(manager.loggers) == 0
    function = getattr(manager, fn_name)
    for n in names:
        function(n)
    assert len(manager.loggers) == len(set(names))
    assert all(i in manager.loggers for i in names)
    assert all(j in manager for j in names)


def test_get_logger_name_caches(build_manager: Callable[..., EpiLog]) -> None:
    """Tests that we retrieve the same logger with the same name."""
    manager: EpiLog = build_manager()
    name: str = "doublethink"
    log_a: logging.Logger = manager.get_logger(name)
    log_b: logging.Logger = manager.get_logger(name)

    assert id(log_a) == id(log_b), "Expected same object."


def test_logging(build_manager: Callable[..., EpiLog]) -> None:
    """Makes certain no errors are raised while logging."""
    manager: EpiLog = build_manager()
    log = manager.get_logger("test")
    log.info("Bob boop beep")


def test_stream(build_manager: Callable[..., EpiLog]) -> None:
    """Tests that the message output by logging is actually written to stream."""
    with StringIO() as stream:
        handler = logging.StreamHandler(stream)
        manager: EpiLog = build_manager(stream=handler)

        log = manager.get_logger("test")
        message = "You are blind to reality and for that I am most proud"
        log.info(message)

        stream.seek(0)
        output = stream.read()
        stream.close()

        assert message in output, "Message not Found in output stream after logging"


def test_level_change(build_manager: Callable[..., EpiLog]) -> None:
    """Tests that modifying the Logging Level accurately filters log output."""
    with StringIO() as stream:
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


def test_format_change(build_manager: Callable[..., EpiLog]) -> None:
    """Tests that modifying the Logging Format accurately Modifies log output Format."""
    with StringIO() as stream:
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


def test_stream_change(build_manager: Callable[..., EpiLog]) -> None:
    """Tests that modifying the Logging Stream writes to the correct Stream."""
    with StringIO() as stream_a, StringIO() as stream_b:
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


def test_stream_change_to_none(build_manager: Callable[..., EpiLog]) -> None:
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
def test_format_instantiation(f, build_manager: Callable[..., EpiLog]) -> None:
    """Tests expected behaviors when instantiating with Formatters."""
    manager: EpiLog = build_manager(formatter=f)
    if f is not None:
        assert manager.formatter == f, "Expected Logging Format to reflect input."
    else:
        assert id(manager.formatter) == id(defaultFormat), "Expected default formatter"


def test_format_error(build_manager: Callable[..., EpiLog]) -> None:
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
def test_levels_instantiation(level, build_manager: Callable[..., EpiLog]) -> None:
    """Tests Expected instantiation Behavior of EpiLog class with Logging Level."""
    manager: EpiLog = build_manager(level=level)
    assert manager.level == level, "Expected Logging Level to be reflect input."


def test_level_error(build_manager: Callable[..., EpiLog]) -> None:
    """Tests that a ValueError is raised when instantiating invalid Logging Level."""
    with pytest.raises(ValueError):
        build_manager(level=-1)


def _confirm_handler_instantiation(
    handler: logging.Handler,
    constructor: Callable[..., EpiLog],
) -> None:
    """Tests Expected instantiation Behavior of EpiLog class with stream."""
    manager: EpiLog = constructor(stream=handler)
    assert manager.stream == handler, "Expected Stream to reflect input."


def test_streamhandler_instantiation(build_manager: Callable[..., EpiLog]) -> None:
    """Tests Expected instantiation Behavior of EpiLog class with stream handler."""
    stream = logging.StreamHandler()
    _confirm_handler_instantiation(stream, build_manager)


def test_filehandler_instantiation(build_manager: Callable[..., EpiLog]) -> None:
    """Tests Expected instantiation Behavior of EpiLog class with file handler."""
    stream = logging.FileHandler("test.log")
    _confirm_handler_instantiation(stream, build_manager)


def test_handlers_error(build_manager: Callable[..., EpiLog]) -> None:
    """Tests that a TypeError is raised when instantiating invalid stream."""
    with pytest.raises(TypeError):
        build_manager(stream="handler")


def test_get_log_by_name(build_manager: Callable[..., EpiLog]) -> None:
    """Tests the special dunder method __get_item__ works as expected."""
    manager: EpiLog = build_manager()
    name = "get_item"
    log: logging.Logger = manager.get_logger(name)

    assert manager[name] == log, "Expected to retrieve the same logger via get item."


def _confirm_removal(cls: EpiLog, name: Union[str, logging.Logger]) -> None:
    if isinstance(name, logging.Logger):
        _name = name.name
    else:
        _name = name

    assert _name in cls.loggers, "Expected logger to be registered"
    assert (
        _name in logging.Logger.manager.loggerDict
    ), "Expected logger to be in logging module registry"

    cls.remove(name)

    assert _name not in cls.loggers, "Expected logger to be removed locally"
    assert (
        _name not in logging.Logger.manager.loggerDict
    ), "Expected logger to be removed from logging module registry"

    # Confirm current stream is not closed
    if hasattr(cls.stream, "_closed"):
        # only available >=python3.10
        assert not cls.stream._closed, "Expected current stream to remain open."
    if hasattr(cls.stream, "stream"):
        assert not cls.stream.stream.closed, "Expected current stream to remain open."


def test_log_removal_by_name(build_manager: Callable[..., EpiLog]) -> None:
    """Test we can remove a logger by providing the name of the logger."""
    manager: EpiLog = build_manager()
    name = "removal_by_name"
    manager.get_logger(name)
    _confirm_removal(manager, name)


def test_log_removal_by_logger(build_manager: Callable[..., EpiLog]) -> None:
    """Test we can remove a logger by providing the logger itself."""
    manager: EpiLog = build_manager()
    name = "removal_by_logger"
    log: logging.Logger = manager.get_logger(name)
    _confirm_removal(manager, log)


def _handle_second_removal(
    stream: IOBase,
    log: logging.Logger,
    manager: EpiLog,
) -> logging.StreamHandler:
    second_handler = logging.StreamHandler(stream)
    log.addHandler(second_handler)

    assert not stream.closed, "Expected stream to be open."
    _confirm_removal(manager, log)

    if hasattr(second_handler, "_closed"):
        assert second_handler._closed, "Expected additional Handler to be closed."

    return second_handler


def test_log_removal_with_additional_handler(
    build_manager: Callable[..., EpiLog],
) -> None:
    """Test that additional handlers and their streams are closed on removal."""
    manager: EpiLog = build_manager()
    name = "removal_by_logger"
    log: logging.Logger = manager.get_logger(name)

    with StringIO() as stream:
        second_handler = _handle_second_removal(stream, log, manager)
        assert stream.closed, "Expected stream to be closed."
        assert second_handler.stream.closed, "Expected stream to be closed."


@pytest.mark.parametrize(
    ["stream"],
    [
        (sys.stderr,),
        (sys.stdin,),
        (sys.stdout,),
    ],
)
def test_log_removal_with_protected_streams(
    build_manager: Callable[..., EpiLog],
    stream: IOBase,
) -> None:
    """Test additional handler is closed on removal, but sys streams remain open."""
    manager: EpiLog = build_manager()
    name = "removal_by_logger"
    log: logging.Logger = manager.get_logger(name)

    second_handler = _handle_second_removal(stream, log, manager)
    assert not stream.closed, "Expected protected stream to remain open."
    assert not second_handler.stream.closed, "Expected protected stream to remain open."
