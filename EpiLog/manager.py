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
"""Primary Logging Manager, EpiLog."""

# Python Dependencies
import logging
from typing import Dict, Optional


defaultFormat = logging.Formatter(
    " | ".join(
        [
            "%(asctime)s",
            "%(name)s",
            "%(levelname)s",
            "%(module)s.%(funcName)s:%(lineno)d",
            "%(message)s",
        ]
    )
)


def _check_level(level: int) -> bool:
    _levels = {
        logging.NOTSET,
        logging.DEBUG,
        logging.INFO,
        logging.WARN,
        logging.ERROR,
        logging.CRITICAL,
    }

    return level in _levels


class EpiLog:
    """Log Manager designed to centralize Local Module or Task level logging control.

    Args:
    ----
        level (int): Logging Level
        stream (logging.Handler): Where logs are written to
        formatter (logging.Formatter): Dictates how to logs are formatted

    Notes:
    -----
        * Natively Supports only a single Stream per instantiated logger.
        * Designed for local control of logging (i.e. Logging events from globally
            imported libraries are not captured)

    """

    __slots__ = ("loggers", "_level", "_formatter", "_stream")

    def __init__(
        self,
        level: int = logging.INFO,
        stream: Optional[logging.Handler] = None,
        formatter: logging.Formatter = defaultFormat,
    ):
        self.loggers: Dict[str, logging.Logger] = {}
        self.stream = stream or logging.StreamHandler()  # noqa: PLE0237
        self.level = level  # noqa: PLE0237
        self.formatter = formatter  # noqa: PLE0237

    def __getitem__(self, item: str) -> logging.Logger:
        """Retrieve Logger by name."""
        return self.loggers[item]

    @property
    def level(self) -> int:
        """Logging Level."""
        return self._level

    @level.setter
    def level(self, value: int):
        """Set Logging Level."""
        if _check_level(value) is False:
            raise ValueError(f"Invalid Logging Level: {value}")

        self._level = value
        self.stream.setLevel(self.level)
        for log in self.loggers.values():
            log.setLevel(self.level)
            # Update the streams to reflect current level
            for handle in log.handlers:
                handle.setLevel(self.level)

    @property
    def formatter(self) -> logging.Formatter:
        """Logging Format."""
        return self._formatter

    @formatter.setter
    def formatter(self, value: Optional[logging.Formatter]):
        """Set Logging Format."""
        if value is None:
            value = defaultFormat

        if not issubclass(value.__class__, logging.Formatter):
            raise TypeError(f"Incorrect Formatter Type: {value.__class__}")

        self._formatter: logging.Formatter = value
        self.stream.setFormatter(self.formatter)
        for log in self.loggers.values():
            for handle in log.handlers:
                handle.setFormatter(self.formatter)

    @property
    def stream(self) -> logging.Handler:
        """Stream Handler for Logging."""
        return self._stream

    @stream.setter
    def stream(self, value: Optional[logging.Handler]):
        """Replace Logging Handler Streams."""
        if value is None:
            value = logging.StreamHandler()

        if not issubclass(value.__class__, (logging.Filterer, logging.Handler)):
            raise TypeError(f"Unsupported Stream Handler: {value.__class__}")

        elif hasattr(self, "_stream"):
            previous = self._stream
            value.setFormatter(self.formatter)
            value.setLevel(self.level)
            self._stream: logging.Handler = value
            for log in self.loggers.values():
                log.removeHandler(previous)
                log.addHandler(self.stream)

        else:
            self._stream = value

    def get_logger(self, name: str) -> logging.Logger:
        """Initialize a new logger."""
        log = logging.getLogger(name)
        log.setLevel(self.level)
        log.addHandler(self.stream)
        self.loggers[name] = log

        return log
