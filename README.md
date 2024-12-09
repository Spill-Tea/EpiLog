<!-- omit in toc -->
# EpiLog

<p>
<a href="https://github.com/Spill-Tea/EpiLog/actions/workflows/python-package.yml?query=branch%3Amain" target="_blank"><img src="https://github.com/Spill-Tea/EpiLog/actions/workflows/python-package.yml/badge.svg?branch=main"></a>
<a href="https://github.com/Spill-Tea/EpiLog/blob/main/LICENSE" target="_blank"><img alt="MIT License" src="https://img.shields.io/github/license/Spill-Tea/EpiLog?style=flat-square&color=%235982b5"></a>
<a href="https://github.com/Spill-Tea/EpiLog/releases/latest" target="_blank"><img alt="GitHub Release" src="https://img.shields.io/github/v/release/Spill-Tea/EpiLog"></a>
<a href="https://pypi.org/project/EpiLog/" target="_blank"><img src="https://badge.fury.io/py/EpiLog.svg?icon=si%3Apython" alt="PyPI version" height="20"></a>
</p>

Logging made simple.

Dispatch multiple loggers identically formatted, and tear them
down just as easily.

<!-- omit in toc -->
## Table of Contents
- [Installation](#installation)
- [Examples](#examples)
- [License](#license)

# Installation
Install from [pypi](https://pypi.org/project/EpiLog/) using pip.

```bash
pip install EpiLog
```

or directly from github, if you want the latest dev

```bash
pip install git+https://github.com/Spill-Tea/EpiLog@main
```

# Examples

Creating a logging manager and dispatch a logger.
```python
import logging
from EpiLog import EpiLog

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
manager: EpiLog = EpiLog(logging.DEBUG, formatter=formatter)
log: logging.Logger = manager.get_logger(__name__)
log.debug("We made a logger!")

# And easily remove the logger
manager.remove(log)
assert __name__ not in manager
```


Benchmarking real time duration to accomplish a function,
or a series of tasks within a facile context manager.

```python
import logging
from EpiLog import Benchmark

message: str = "Long Task Complete"
level: int = logging.INFO  # level to emit message
with Benchmark(log, message, level):
    perform_long_task(...)

```
Note, that if the level used to emit the message is below
your logger level, then no message will be emitted.

# License

[MIT](LICENSE)
