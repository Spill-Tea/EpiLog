"""
    EpiLog/tests/test_manager.py

"""
import os
import logging
import pytest
from io import StringIO
from EpiLog.manager import EpiLog


@pytest.mark.parametrize("names", [
    ("a", "b", "c"),
    ("b", "c", "d", "e")
])
def test_get_logger(names):
    manager = EpiLog()
    assert len(manager.loggers) == 0

    for n in names:
        manager.get_logger(n)
    assert len(manager.loggers) == len(names)
    assert all(i in manager.loggers for i in names)


def test_logging():
    manager = EpiLog()
    log = manager.get_logger("test")
    log.info("Bob boop beep")


def test_stream():
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
    stream = StringIO()

    handler = logging.StreamHandler(stream)
    manager = EpiLog(level=logging.INFO, stream=handler)
    log = manager.get_logger("test")

    message = "I would say that he's blessedly unburdened with the complications of a university education."
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


@pytest.mark.parametrize("f", [
    None,
    pytest.param("Failure", marks=pytest.mark.xfail(raises=TypeError)),
    logging.Formatter("%(name)s | %(levelname)s | %(message)s"),
])
def test_format(f):
    manager = EpiLog(formatter=f)
    manager.formatter = f


@pytest.mark.parametrize("level", [
    logging.NOTSET,
    logging.DEBUG,
    logging.INFO,
    logging.WARN,
    logging.ERROR,
    logging.CRITICAL,
    pytest.param(-1, marks=pytest.mark.xfail(raises=ValueError))
])
def test_levels(level):
    manager = EpiLog(level=level)
    assert manager.level == level


@pytest.mark.parametrize("handler", [
    logging.FileHandler("test.log"),
    logging.StreamHandler(),
    pytest.param("handler", marks=pytest.mark.xfail(raises=TypeError))
])
def test_handlers(handler):
    manager = EpiLog(stream=handler)

    # Cleanup by removing file created by file handler
    if isinstance(handler, logging.FileHandler):
        os.remove(handler.baseFilename)

    assert manager.stream == handler
