"""
Shared test fixtures for djb core tests.

See __init__.py for the full list of available fixtures and utilities.

Auto-enabled fixtures (applied to all tests automatically):
    clean_djb_env - Ensures a clean environment by removing DJB_* env vars
"""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest

# Environment variables that may be set by CLI test fixtures
_DJB_ENV_VARS = [
    "DJB_PROJECT_DIR",
    "DJB_PROJECT_NAME",
    "DJB_NAME",
    "DJB_EMAIL",
    "DJB_MODE",
    "DJB_TARGET",
    "DJB_HOSTNAME",
]


@pytest.fixture(autouse=True)
def clean_djb_env() -> Generator[None, None, None]:
    """Ensure a clean environment for config tests.

    This fixture removes all DJB_* environment variables before each test
    and restores the original state afterward. This prevents autouse fixtures
    from other test directories (like cli/tests) from affecting these tests.
    """
    old_env = {k: os.environ.get(k) for k in _DJB_ENV_VARS}
    for k in _DJB_ENV_VARS:
        os.environ.pop(k, None)
    try:
        yield
    finally:
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
