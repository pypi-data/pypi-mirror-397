"""Shared test fixtures for djb.cli.utils tests."""

from __future__ import annotations

import os
import pty
import sys

import pytest


@pytest.fixture
def pty_stdin():
    """Fixture that creates a PTY and temporarily replaces stdin.

    This fixture properly saves and restores stdin state between tests,
    avoiding pollution that can occur with manual save/restore.

    Yields the master fd which can be written to simulate user input.
    """
    # Create PTY pair
    master_fd, slave_fd = pty.openpty()

    # Save original stdin state
    original_stdin_fd = os.dup(0)

    # Replace stdin with slave end of PTY
    os.dup2(slave_fd, 0)
    os.close(slave_fd)  # Close original fd since we dup2ed it
    sys.stdin = os.fdopen(0, "r", closefd=False)

    yield master_fd

    # Restore original stdin
    # First, close the current sys.stdin without closing fd 0
    sys.stdin.close()
    # Restore fd 0 to original
    os.dup2(original_stdin_fd, 0)
    os.close(original_stdin_fd)
    # Recreate sys.stdin from restored fd 0
    sys.stdin = os.fdopen(0, "r", closefd=False)
    # Close master end
    os.close(master_fd)
