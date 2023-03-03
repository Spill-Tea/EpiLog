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
"""
    EpiLog/benchmark.py

"""
# Python Dependencies
import logging
from time import perf_counter_ns


class BenchMark:
    """Context Manager to Benchmark any process through a log."""
    __slots__ = ("enabled", "log", "description", "t0")

    def __init__(self, log: logging.Logger, description: str, level: int = logging.INFO):
        self.enabled = log.isEnabledFor(level)
        self.log = log
        self.description = description
        self.t0 = None

    def __enter__(self):
        if self.enabled:
            self.t0 = perf_counter_ns()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logging.error("Traceback...:\n", exc_info=(exc_type, exc_val, exc_tb))

        if not self.enabled:
            return

        end = perf_counter_ns()
        elapsed = (end - self.t0) / 1_000_000
        self.log.info("%s: %.4fms", self.description, elapsed)
