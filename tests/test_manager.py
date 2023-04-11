"""
    EpiLog/tests/test_manager.py

"""
import pytest

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

