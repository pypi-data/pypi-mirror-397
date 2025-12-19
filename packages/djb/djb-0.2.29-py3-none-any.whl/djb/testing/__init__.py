"""
djb.testing - Reusable testing utilities for djb-based projects.

Provides testing utilities that can be imported by host projects
for type checking and E2E test management.

Quick start - Type checking:
    # In your test file (e.g., tests/test_types.py):
    from djb.testing import test_typecheck

    # Pytest discovers and runs the test automatically

Quick start - E2E test markers:
    # In your conftest.py:
    from djb.testing import (
        pytest_addoption,
        pytest_configure,
        pytest_collection_modifyitems,
    )

    # This adds --run-e2e and --only-e2e flags to pytest

Public API:
    Type checking:
        test_typecheck - Importable test function for running pyright

    Pytest hooks (for E2E test markers):
        pytest_addoption - Add --run-e2e and --only-e2e options
        pytest_configure - Register e2e marker
        pytest_collection_modifyitems - Skip e2e tests by default
"""

from __future__ import annotations

from djb.testing.pytest_e2e import (
    pytest_addoption,
    pytest_collection_modifyitems,
    pytest_configure,
)
from djb.testing.typecheck import test_typecheck

__all__ = [
    # Type checking
    "test_typecheck",
    # Pytest E2E hooks
    "pytest_addoption",
    "pytest_collection_modifyitems",
    "pytest_configure",
]
