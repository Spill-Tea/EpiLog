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
from typing import Dict, Iterator, Tuple, Union


@dataclass
class Unit:
    """Unit comparing string id to a modifier of the next unit.

    Args:
        unit (str): name of unit
        base (int): value of unit
        modifier (int | None): multiplier describing 1 of next unit

    """

    unit: str
    base: int = 1
    modifier: Union[int, None] = None


class Units:
    """Container of Units.

    Args:
        units (Unit): unit defintions

    """

    units: Tuple[Unit, ...]

    def __init__(self, *units: Unit):
        self.units = units
        self._update()

    def _update(self):
        for n, current in enumerate(self.units[1:]):
            previous = self.units[n]
            current.base = previous.base * previous.modifier

    def __iter__(self) -> Iterator[Unit]:
        yield from self.units

    def convert_units(self, value: int) -> Tuple[float, str]:
        """Convert base unit into most relevant unit."""
        new_time: float = float(value)
        text: str = ""

        for u in self:
            new_time = value / u.base
            text = u.unit
            if u.modifier is None or new_time < u.modifier:
                break

        return new_time, text

    def breakdown_units(self, value: int) -> Dict[str, int]:
        """Split base value into component unit bins."""
        data: Dict[str, int] = {}
        for unit in reversed(self.units):
            data[unit.unit], value = divmod(value, unit.base)

        return data


NS_UNITS = Units(
    Unit(unit="ns", modifier=1000),
    Unit(unit="us", modifier=1000),
    Unit(unit="ms", modifier=1000),
    Unit(unit="s", modifier=60),
    Unit(unit="min", modifier=60),
    Unit(unit="hr", modifier=24),
    Unit(unit="days", modifier=7),
    Unit(unit="weeks"),
)


class BenchMark:
    """Context Manager to Benchmark any process through a log.

    Args:
        log (logging.Logger):
        description (str): Message used to describe actions performed during benchmark.
        level (int): Logging Level

    Attributes:
        enabled (bool): If Benchmark level is compatible with log level to emit message.
        t0 (int): Entry time to benchmark suite.

    Examples:
        ```python
        import logging
        from EpiLog import Benchmark
        log: logging.Logger = logging.getLogger("name")
        message: str = "this is a message"
        with Benchmark(log, message, logging.INFO):
            perform_task(...)
        ```

    """

    __slots__ = ("description", "enabled", "level", "log", "t0")

    level: int
    enabled: bool
    log: logging.Logger
    description: str
    t0: int

    def __init__(
        self,
        log: logging.Logger,
        description: str,
        level: int = logging.INFO,
    ) -> None:
        self.level = level
        self.enabled = log.isEnabledFor(self.level)
        self.log = log
        self.description = description
        self.t0 = 0

    def __enter__(self) -> "BenchMark":
        if self.enabled:
            self.t0 = perf_counter_ns()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        end: int = perf_counter_ns()

        if exc_type is not None:
            self.log.error("Traceback:", exc_info=(exc_type, exc_val, exc_tb))
            return

        if not self.enabled:
            return

        elapsed, unit = NS_UNITS.convert_units(end - self.t0)
        self.log.log(self.level, "%s: (%.4f %s)", self.description, elapsed, unit)
