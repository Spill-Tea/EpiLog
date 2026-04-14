"""Unit tests to examine the Expected Behavior of the EpiLog Logging Manager."""

from __future__ import annotations

import logging
import sys
from io import IOBase, StringIO
from typing import Callable, Optional, Tuple, Union

import pytest

from EpiLog import EpiLog
from EpiLog.manager import defaultFormat

from .conftest import _assert_msg_in_output


# def _assert_msg_in_output(stream: IOBase, msg: str) -> None:
#     stream.seek(0)
#     output: str = stream.read()
#     assert msg in output, "Message not found in output stream after logging."


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
    function: Callable[[str], logging.Logger] = getattr(manager, fn_name)
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
    assert len(manager.loggers) == 1, "Expected a single key entry in logger registry."


def test_logging(build_manager: Callable[..., EpiLog]) -> None:
    """Makes certain no errors are raised while logging."""
    manager: EpiLog = build_manager()
    log: logging.Logger = manager.get_logger("test")
    log.info("Bob boop beep")


def test_stream(build_manager: Callable[..., EpiLog]) -> None:
    """Tests that the message output by logging is actually written to stream."""
    with StringIO() as stream:
        handler = logging.StreamHandler(stream)
        manager: EpiLog = build_manager(stream=handler)

        log: logging.Logger = manager.get_logger("test")
        message: str = "You are blind to reality and for that I am most proud"
        log.info(message)

        _assert_msg_in_output(stream, message)


def test_level_change(build_manager: Callable[..., EpiLog]) -> None:
    """Tests that modifying the Logging Level accurately filters log output."""
    with StringIO() as stream:
        handler = logging.StreamHandler(stream)

        manager: EpiLog = build_manager(level=logging.INFO, stream=handler)
        log: logging.Logger = manager.get_logger("test")

        message: str = (
            "I would say that he's blessedly unburdened with the complications of a"
            " university education."
        )
        log.debug(message)
        assert stream.tell() == 0, "Expected no output at current level."
        with pytest.raises(AssertionError):
            _assert_msg_in_output(stream, message)

        # Then repeat after Changing level
        manager.level = logging.DEBUG
        log.debug(message)
        _assert_msg_in_output(stream, message)


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

        _assert_msg_in_output(stream, f"INFO | {message}\n")


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
        log: logging.Logger = manager.get_logger("test")

        # Modify Stream
        manager.stream = handler_b
        assert manager.stream == handler_b, "Unexpected Stream."

        message: str = (
            "You humans have so many emotions! You only need two: anger and confusion!"
        )
        expected: str = f"INFO | {message}\n"
        log.info(message)

        # Test first stream (where we do not expect message output)
        with pytest.raises(AssertionError):
            _assert_msg_in_output(stream_a, message)

        # Test Second, Expected stream
        _assert_msg_in_output(stream_b, expected)


def test_stream_change_to_none(build_manager: Callable[..., EpiLog]) -> None:
    """Confirm that attempts to set the stream to none result in default stream."""
    manager: EpiLog = build_manager()
    assert manager.stream is not None, "Expected Default Stream to instantiate."
    previous_id: int = id(manager.stream)

    manager.stream = None  # type: ignore[assignment]
    assert manager.stream is not None, "Expected Default Stream to kick in."
    assert isinstance(manager.stream, (logging.Handler, logging.Filterer)), (
        "Unexpected stream type."
    )

    assert id(manager.stream) != previous_id, "Expected new stream instance."


@pytest.mark.parametrize(
    "f",
    [
        None,
        logging.Formatter("%(name)s | %(levelname)s | %(message)s"),
    ],
)
def test_format_instantiation(
    f: Optional[logging.Formatter],
    build_manager: Callable[..., EpiLog],
) -> None:
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
    name: str = "get_item"
    log: logging.Logger = manager.get_logger(name)

    assert manager[name] == log, "Expected to retrieve the same logger via get item."


def _confirm_removal(cls: EpiLog, name: Union[str, logging.Logger]) -> None:
    _name: str = name.name if isinstance(name, logging.Logger) else name
    assert _name in cls.loggers, "Expected logger to be registered"
    assert _name in logging.Logger.manager.loggerDict, (
        "Expected logger to be in logging module registry"
    )

    cls.remove(name)

    assert _name not in cls.loggers, "Expected logger to be removed locally"
    assert _name not in logging.Logger.manager.loggerDict, (
        "Expected logger to be removed from logging module registry"
    )

    # Confirm current stream is not closed
    if hasattr(cls.stream, "_closed"):
        # only available >=python3.10
        assert not cls.stream._closed, (  # pyright: ignore
            "Expected current stream to remain open."
        )
    if hasattr(cls.stream, "stream"):
        assert not cls.stream.stream.closed, (  # pyright: ignore
            "Expected current stream to remain open."
        )


def test_log_removal_by_name(build_manager: Callable[..., EpiLog]) -> None:
    """Test we can remove a logger by providing the name of the logger."""
    manager: EpiLog = build_manager()
    name: str = "removal_by_name"
    manager.get_logger(name)
    _confirm_removal(manager, name)


def test_log_removal_by_logger(build_manager: Callable[..., EpiLog]) -> None:
    """Test we can remove a logger by providing the logger itself."""
    manager: EpiLog = build_manager()
    name: str = "removal_by_logger"
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
        assert second_handler._closed, (  # pyright: ignore
            "Expected additional Handler to be closed."
        )

    return second_handler


def test_log_removal_with_additional_handler(
    build_manager: Callable[..., EpiLog],
) -> None:
    """Test that additional handlers and their streams are closed on removal."""
    manager: EpiLog = build_manager()
    name: str = "removal_by_logger"
    log: logging.Logger = manager.get_logger(name)

    with StringIO() as stream:
        second: logging.StreamHandler = _handle_second_removal(stream, log, manager)
        assert stream.closed, "Expected stream to be closed."
        assert second.stream.closed, "Expected stream to be closed."


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
    name: str = "removal_by_logger"
    log: logging.Logger = manager.get_logger(name)

    second_handler: logging.StreamHandler = _handle_second_removal(stream, log, manager)
    assert not stream.closed, "Expected protected stream to remain open."
    assert not second_handler.stream.closed, "Expected protected stream to remain open."
