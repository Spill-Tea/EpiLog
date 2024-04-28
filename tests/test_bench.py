"""Test Expected Behavior of the EpiLog Benchmark Module."""

from io import StringIO
from logging import StreamHandler

from EpiLog.benchmark import BenchMark
from EpiLog.manager import EpiLog


def test_empty_benchmark():
    """Tests that an Empty Benchmark context manager class correctly logs message."""
    stream = StringIO()

    handler = StreamHandler(stream)
    manager = EpiLog(stream=handler)
    log = manager.get_logger("test")
    msg = "I'm positively bedeviled with meetings et cetera"

    with BenchMark(log, msg):
        ...

    stream.seek(0)
    output = stream.read()

    assert msg in output, "Message not Found in output stream after logging"
    assert "Traceback" not in output, "Error raised during use of context manager."
