"""CLI context for passing global options to subcommands."""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, ParamSpec, TypeVar

import click

if TYPE_CHECKING:
    from djb.config import DjbConfig

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class CliContext:
    """Context object passed through click's ctx.obj.

    This dataclass holds global CLI options that any subcommand can access.
    Use ctx.ensure_object(CliContext) in the main CLI group and access
    values via ctx.obj.<field_name> in subcommands.

    Subcommand groups can specialize the context by:
    1. Saving the parent context: `parent_ctx = ctx.obj`
    2. Creating their specialized context: `ctx.obj = CliHealthContext()`
    3. Copying parent fields: `ctx.obj.__dict__.update(parent_ctx.__dict__)`
    4. Setting specialized fields: `ctx.obj.fix = fix`

    Example:
        @click.pass_context
        def my_command(ctx: click.Context):
            if ctx.obj.verbose:
                click.echo("Verbose mode enabled")
    """

    # Global options (set by djb_cli)
    log_level: str = "info"
    verbose: bool = False
    quiet: bool = False
    # Config is set by djb_cli before any subcommand runs.
    # Default is None but typed as DjbConfig since commands can assume it exists.
    config: DjbConfig = field(default=None)  # type: ignore[assignment]

    # Scope options (useful for multiple commands)
    scope_frontend: bool = False
    scope_backend: bool = False


@dataclass
class CliHealthContext(CliContext):
    """Specialized context for `djb health` command group.

    Inherits all global options from CliContext and adds health-specific options.
    """

    fix: bool = False
    cov: bool = False


@dataclass
class CliHerokuContext(CliContext):
    """Specialized context for `djb deploy heroku` command group.

    Inherits all global options from CliContext and adds heroku-specific options.
    """

    app: str | None = None


def pass_cli_context(f: Callable[..., R]) -> Callable[..., R]:
    """Decorator that passes CliContext as the first argument to a command.

    Use instead of @click.pass_context when you only need CliContext:

        @click.command()
        @pass_cli_context
        def my_command(cli_ctx: CliContext):
            project_dir = cli_ctx.config.project_dir
            ...

    The decorated function receives CliContext directly, avoiding the need
    to call _get_cli_context(ctx) in every command.
    """

    @functools.wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        ctx = click.get_current_context()
        cli_ctx = ctx.obj
        assert isinstance(cli_ctx, CliContext), "Expected CliContext at ctx.obj"
        return f(cli_ctx, *args, **kwargs)

    return wrapper


def pass_health_context(f: Callable[..., R]) -> Callable[..., R]:
    """Decorator that passes CliHealthContext as the first argument.

    Use in health subcommands that need the specialized health context:

        @health.command()
        @pass_health_context
        def lint(health_ctx: CliHealthContext):
            fix = health_ctx.fix
            ...
    """

    @functools.wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        ctx = click.get_current_context()
        health_ctx = ctx.obj
        assert isinstance(health_ctx, CliHealthContext), "Expected CliHealthContext at ctx.obj"
        return f(health_ctx, *args, **kwargs)

    return wrapper
