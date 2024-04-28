"""Pytest Fixtures and Utilities."""

import logging

import pytest

from EpiLog.manager import EpiLog


def teardown_logs(epilog: EpiLog):
    """Handle Teardown of EpiLog Manager."""
    names = epilog.loggers.keys()
    epilog.loggers.clear()

    # Remove names from Global Logging Root
    for key in names:
        logging.Logger.manager.loggerDict.pop(key)


@pytest.fixture
def build_manager():
    """Construct an EpiLog Instance and Handles Tear down of creating new Loggers."""
    instance: EpiLog = None

    def builder(*args, **kwargs):
        nonlocal instance
        instance = EpiLog(*args, **kwargs)
        return instance

    yield builder

    if instance is not None:
        teardown_logs(instance)
