# MIT License

# Copyright (c) 2023 Spill-Tea

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Simple context manager to log procedure operation duration, for benchmark."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from time import perf_counter_ns


@dataclass
class UnitTime:
    """Unit Time comparing string id to a modifier of next unit."""

    unit: str
    base: int = 1
    modifier: int | None = None


NS_UNITS = (
    UnitTime(unit="ns", modifier=1000),
    UnitTime(unit="us", modifier=1000),
    UnitTime(unit="ms", modifier=1000),
    UnitTime(unit="s", modifier=60),
    UnitTime(unit="min", modifier=60),
    UnitTime(unit="hr", modifier=24),
    UnitTime(unit="days", modifier=7),
    UnitTime(unit="weeks", modifier=None),
)


def _update():
    for n, current in enumerate(NS_UNITS[1:]):
        previous = NS_UNITS[n]
        current.base = previous.base * previous.modifier


_update()


def convert_units(time_ns: int) -> tuple[float, str]:
    """Get More Accurate Timing."""
    new_time: float = float(time_ns)
    text: str = "ns"

    for u in NS_UNITS:
        new_time = time_ns / u.base
        text = u.unit
        if u.modifier is None or new_time < u.modifier:
            break

    return new_time, text


def breakdown_units(value: int) -> dict[str, int]:
    """Split ns value into component time bins."""
    data = {}
    for unit in reversed(NS_UNITS):
        data[unit.unit], value = divmod(value, unit.base)
    return data


class BenchMark:
    """Context Manager to Benchmark any process through a log.

    Args:
    ----
        log (logging.Logger):
        description (str): Message used to describe actions performed during benchmark.
        level (int): Logging Level

    Attributes:
    ----------
        enabled (bool): If Benchmark level is compatible with log level to emit message.
        t0 (int): Entry time to benchmark suite.

    """

    __slots__ = ("description", "enabled", "level", "log", "t0")

    level: int
    enabled: bool
    log: logging.Logger
    description: str
    t0: int

    def __init__(
        self, log: logging.Logger, description: str, level: int = logging.INFO
    ):
        self.level = level
        self.enabled = log.isEnabledFor(self.level)
        self.log = log
        self.description = description
        self.t0 = 0

    def __enter__(self):
        if self.enabled:
            self.t0 = perf_counter_ns()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.log.error("Traceback:", exc_info=(exc_type, exc_val, exc_tb))
            return

        if not self.enabled:
            return

        end = perf_counter_ns()
        elapsed, unit = convert_units(end - self.t0)
        self.log.log(self.level, "%s: (%.4f %s)", self.description, elapsed, unit)
