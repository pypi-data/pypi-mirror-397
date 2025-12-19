"""
djb.testing - Reusable testing utilities for djb-based projects.

Exports:
    test_typecheck - Importable test function for running pyright
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
