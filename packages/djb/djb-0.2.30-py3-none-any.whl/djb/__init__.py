"""
djb - Django + Bun deployment platform.

A simplified, self-contained deployment platform for Django applications.

Public API:
    __version__ - Package version string

    Logging:
        setup_logging - Initialize the djb logging system
        get_logger - Get a logger instance for a module
        Level - Enum of log levels (DEBUG, INFO, etc.)
        CliLogger - Logger class for CLI output formatting

    Config:
        config - Singleton configuration object

    CLI:
        get_cli_epilog - Get djb epilog text for embedding in host project CLIs
"""

from __future__ import annotations

from djb._version import __version__
from djb.cli.epilog import get_cli_epilog
from djb.cli.logging import CliLogger, Level, get_logger, setup_logging
from djb.config import config


__all__ = [
    "__version__",
    # Logging
    "CliLogger",
    "Level",
    "get_logger",
    "setup_logging",
    # Config
    "config",
    # CLI
    "get_cli_epilog",
]
