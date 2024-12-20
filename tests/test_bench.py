"""Test Expected Behavior of the EpiLog Benchmark Module."""

from __future__ import annotations

import logging
from io import StringIO
from typing import Generator, Tuple

import pytest

from EpiLog import EpiLog
from EpiLog.benchmark import NS_UNITS, BenchMark, Units


@pytest.fixture
def construct(build_manager) -> Generator[Tuple[StringIO, EpiLog], None, None]:
    """Construct EpiLog Log Manager with standard Fixings."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    form = logging.Formatter("%(levelname)s | %(message)s")
    manager = build_manager(stream=handler, formatter=form)

    yield stream, manager

    stream.close()
    assert stream.closed, "Expected Stream to be Closed."


def test_empty_benchmark(construct: Tuple[StringIO, EpiLog]) -> None:
    """Tests that an Empty Benchmark context manager class correctly logs message."""
    stream, manager = construct
    manager.level = logging.INFO

    log = manager.get_logger("test")
    msg = "I'm positively bedeviled with meetings et cetera"
    expected = f"INFO | {msg}"

    with BenchMark(log, msg) as b:
        assert b.enabled, "Expected Logging to be Enabled on Benchmark Class."

    stream.seek(0)
    output = stream.read()

    assert msg in output, "Message not Found in output stream after logging."
    assert expected in output, "Message Format not found in Output Stream."
    assert "Traceback" not in output, "Error raised during use of context manager."


def test_enabled(construct: Tuple[StringIO, EpiLog]) -> None:
    """Tests that a Benchmark Logging Level below a Log Level does not log."""
    stream, manager = construct
    manager.level = logging.CRITICAL

    log = manager.get_logger("disabled")
    msg = "That's exactly the kind of paranoia that makes me weary of spending time "
    msg += "with you."

    with BenchMark(log, msg, logging.DEBUG) as b:
        assert not b.enabled, "Expected Logging to be Disabled on Benchmark Class."

    stream.seek(0)
    output = stream.read()
    assert msg not in output, "Message Found in output stream after disabled Benchmark."


def test_error(construct: Tuple[StringIO, EpiLog]) -> None:
    """Test that an error message is emitted when one occurs during context."""
    stream, manager = construct
    manager.level = logging.DEBUG
    log = manager.get_logger("errors")

    with pytest.raises(AssertionError):
        with BenchMark(log, "msg", logging.DEBUG):
            assert False, "We are Intentionally raising an error"  # noqa: B011

    stream.seek(0)
    output = stream.read()
    assert "ERROR" in output, "Expected Error Level Log Emitted"
    assert "Traceback" in output, "Expected Log message to include traceback info."


def test_empty_convert_units():
    """Test branch point in Units class to calculate unit conversion method."""
    instance = Units()
    value: float = 1.2
    res, u = instance.convert_units(value)

    assert res == value, "Expected same value."
    assert u == "", "Expected empty unit string."


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        (50, (50.0, "ns")),
        (1000, (1.0, "us")),
        (500_000, (500.0, "us")),
        (1_000_000, (1.0, "ms")),
        (1_000_000_000, (1.0, "s")),
        (60_000_000_000, (1.0, "min")),
        (3_600_000_000_000, (1.0, "hr")),
        (86_400_000_000_000, (1.0, "days")),
        (604_800_000_000_000, (1.0, "weeks")),
    ],
)
def test_units_convert_units(value: int, expected: float):
    """Test that we correctly convert units to largest relevant bin."""
    result = NS_UNITS.convert_units(value)
    assert result == expected, "Unexpected conversion."


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        (50, {"ns": 50}),
        (1000, {"us": 1}),
        (1_000_000, {"ms": 1}),
        (5_050_000, {"ms": 5, "us": 50}),
        (5_050_000, {"ms": 5, "us": 50}),
        (1_005_050_000, {"s": 1, "ms": 5, "us": 50}),
    ],
)
def test_breakdown(value: int, expected: dict) -> None:
    """Test Breakdown of ns into appropriate time bins."""
    result = NS_UNITS.breakdown_units(value)
    container = dict((i.unit, 0) for i in NS_UNITS)
    container.update(expected)

    assert result == container, "Expected Equal Output."
