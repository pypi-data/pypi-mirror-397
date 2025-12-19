"""
djb config CLI - Manage djb configuration.

Provides a discoverable, documented interface for viewing and modifying
djb settings. Each config option is a subcommand with its own documentation.
"""

from __future__ import annotations

import click

from djb.cli.logging import get_logger
from djb.config import config

logger = get_logger(__name__)


@click.group("config")
def config_group() -> None:
    """Manage djb configuration.

    View and modify djb settings. Each subcommand manages a specific
    configuration option with its own documentation.

    \b
    Examples:
      djb config seed_command                     # Show current value
      djb config seed_command myapp.cli:seed      # Set seed command
    """
    pass


@config_group.command("seed_command")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the seed_command setting.",
)
def config_seed_command(value: str | None, delete: bool) -> None:
    """Configure the host project's seed command.

    The seed command is a Click command from your project that djb will:

    \b
    * Register as 'djb seed' for manual execution
    * Run automatically during 'djb init' after migrations

    The value should be a module:attribute path to a Click command.

    \b
    Examples:
      djb config seed_command                           # Show current
      djb config seed_command myapp.cli.seed:seed       # Set command
      djb config seed_command --delete                  # Remove setting

    \b
    Your seed command should:
      * Be a Click command (decorated with @click.command())
      * Handle Django setup internally (call django.setup())
      * Be idempotent (safe to run multiple times)
    """
    if delete:
        # Remove the setting
        if "seed_command" in config:
            del config.seed_command
            logger.done("seed_command removed")
        else:
            logger.info("seed_command: (not set)")
    elif value is None:
        # Show current value
        if "seed_command" in config:
            logger.info(f"seed_command: {config.seed_command}")
        else:
            logger.info("seed_command: (not set)")
    else:
        # Validate format (should contain exactly one colon)
        if ":" not in value:
            raise click.ClickException(
                f"Invalid format: '{value}'. Expected 'module.path:attribute' "
                "(e.g., 'myapp.cli.seed:seed')"
            )
        parts = value.split(":")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise click.ClickException(
                f"Invalid format: '{value}'. Expected 'module.path:attribute' "
                "(e.g., 'myapp.cli.seed:seed')"
            )

        # Set new value
        config.seed_command = value
        logger.done(f"seed_command set to: {value}")
