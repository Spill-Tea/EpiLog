"""
    EpiLog/tests/test_bench.py

"""
from io import StringIO
from logging import StreamHandler
from EpiLog.manager import EpiLog
from EpiLog.benchmark import BenchMark


def test_mark():
    stream = StringIO()

    handler = StreamHandler(stream)
    manager = EpiLog(stream=handler)
    log = manager.get_logger("test")
    msg = "I’m positively bedeviled with meetings et cetera"

    with BenchMark(log, msg) as b:
        ...

    stream.seek(0)
    output = stream.read()

    assert msg in output, "Message not Found in output stream after logging"
    assert "Traceback" not in output, "Error raised during use of context manager."
