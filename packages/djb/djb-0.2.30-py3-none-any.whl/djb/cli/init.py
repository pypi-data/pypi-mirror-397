"""
djb init CLI - Initialize djb development environment.

Provides commands for setting up system dependencies, Python packages, and frontend tooling.
"""

from __future__ import annotations

import readline  # noqa: F401 - enables line editing for input()
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import click

from djb.cli.db import init_database
from djb.cli.logging import get_logger
from djb.cli.secrets import _ensure_prerequisites as ensure_secrets_prerequisites
from djb.cli.seed import run_seed_command
from djb.cli.utils import check_cmd, run_cmd
from djb.config import (
    LOCAL,
    PROJECT,
    config,
    get_config,
    get_config_path,
    get_project_name_from_pyproject,
    load_merged_config,
    migrate_legacy_config,
)
from djb.secrets import init_gpg_agent_config, init_or_upgrade_secrets

logger = get_logger(__name__)

# Intentionally permissive email regex - strict validation isn't needed here
# since we just need a reasonable email format for git config and secrets.
EMAIL_REGEX = re.compile(r"^.+@.+\..+$")


def _get_clipboard_command() -> str:
    """Get the appropriate clipboard command for the current platform.

    Returns:
        'clip.exe' on WSL2, 'pbcopy' on macOS, 'xclip' on Linux.
    """
    # Check for WSL2 first
    try:
        with open("/proc/version", "r") as f:
            if "microsoft" in f.read().lower():
                return "clip.exe"
    except (FileNotFoundError, PermissionError):
        pass

    # macOS
    if sys.platform == "darwin":
        return "pbcopy"

    # Linux fallback
    return "xclip"


def _get_git_config(key: str) -> str | None:
    """Get a value from git config."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", key],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, OSError):
        pass
    return None


def _set_git_config(key: str, value: str) -> bool:
    """Set a value in git config (global)."""
    try:
        result = subprocess.run(
            ["git", "config", "--global", key, value],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def _configure_field(
    field: str,
    sources: list[tuple[str, Callable[[], str | None]]],
    *,
    config_attr: str | None = None,
    prompt: str | None = None,
    default: str = "",
    validator: re.Pattern[str] | None = None,
    required: bool = True,
) -> tuple[str | None, str | None]:
    """Configure a field from prioritized sources, falling back to prompt.

    Args:
        field: Display name (e.g., "name", "email", "hostname")
        sources: List of (source_name, getter) in priority order. Getters are
            called lazily, so later sources won't be evaluated if earlier ones
            have a value.
        config_attr: Attribute name on config singleton (default: field)
        prompt: Prompt text (default: "Enter your {field}")
        default: Default value for prompt
        validator: Optional regex pattern for validation
        required: If True, warn when empty

    Returns:
        Tuple of (value, source_name where value came from)
    """
    if config_attr is None:
        config_attr = field

    # Try each source in priority order (lazy evaluation)
    for source_name, get_value in sources:
        value = get_value()
        if value:
            # Validate source values (skip invalid ones to try next source)
            if validator and not validator.match(value):
                logger.warning(f"Invalid {field} in {source_name}: {value}")
                continue
            if source_name == "djb config":
                logger.info(f"{field.title()}: {value}")
            else:
                setattr(config, config_attr, value)
            return value, source_name

    # No source had a value - prompt user (using input() for readline support)
    prompt_text = prompt or f"Enter your {field}"

    for _ in range(3):
        if default:
            display = f"{prompt_text} [{default}]: "
        else:
            display = f"{prompt_text}: "
        try:
            entered = input(display).strip() or default
        except (EOFError, KeyboardInterrupt):
            print()  # newline after ^C/^D
            return None, None
        if not entered:
            if required:
                logger.warning(f"{field.title()} is required.")
            continue
        if validator and not validator.match(entered):
            logger.warning(f"Invalid {field} format. Please try again.")
            continue
        setattr(config, config_attr, entered)
        logger.done(f"{field.title()} saved: {entered}")
        return entered, "prompt"

    logger.warning(f"{field.title()} skipped.")
    return None, None


def _configure_user_identity() -> tuple[str | None, str | None]:
    """Configure user identity (name and email).

    Checks djb config first, then git config, then prompts user.
    Syncs prompted values back to git config.

    Returns:
        Tuple of (name, email), either or both may be None if skipped.
    """
    logger.next("Configuring user identity")
    config_path = get_config_path(LOCAL)
    copied_from_git = []

    name, name_source = _configure_field(
        "name",
        sources=[
            ("djb config", lambda: config.name),
            ("git config", lambda: _get_git_config("user.name")),
        ],
    )
    if name_source == "git config":
        copied_from_git.append("name")
    elif name_source == "prompt" and name:
        _set_git_config("user.name", name)

    email, email_source = _configure_field(
        "email",
        sources=[
            ("djb config", lambda: config.email),
            ("git config", lambda: _get_git_config("user.email")),
        ],
        validator=EMAIL_REGEX,
    )
    if email_source == "git config":
        copied_from_git.append("email")
    elif email_source == "prompt" and email:
        _set_git_config("user.email", email)

    if copied_from_git:
        logger.info(f"Copied {' and '.join(copied_from_git)} from git config")

    if name or email:
        logger.info(f"Config saved to: {config_path}")

    return name, email


def _configure_project_name(project_root: Path) -> str | None:
    """Configure project name."""
    logger.next("Configuring project name")
    # Note: check raw config file, not config.project_name (which has pyproject fallback)
    value, source = _configure_field(
        "project name",
        sources=[
            ("djb config", lambda: load_merged_config(project_root).get("project_name")),
            ("pyproject.toml", lambda: get_project_name_from_pyproject(project_root)),
        ],
        config_attr="project_name",
        prompt="Enter project name",
        default=project_root.name,
    )
    if source == "pyproject.toml":
        logger.info("Copied project name from pyproject.toml")
    return value


def _configure_hostname(project_name: str | None) -> str | None:
    """Configure hostname for deployment."""
    logger.next("Configuring hostname")
    default = f"{project_name}.com" if project_name else ""
    value, _ = _configure_field(
        "hostname",
        sources=[("djb config", lambda: config.hostname)],
        prompt="Enter production hostname",
        default=default,
    )
    return value


def _find_settings_file(project_root: Path) -> Path | None:
    """Find the Django settings.py file in the project.

    Searches for settings.py in subdirectories of project_root that look like
    Django project directories (contain __init__.py).

    Returns:
        Path to settings.py if found, None otherwise.
    """
    # Look for directories containing settings.py
    for item in project_root.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            settings_path = item / "settings.py"
            init_path = item / "__init__.py"
            # Must have both settings.py and __init__.py to be a Django project
            if settings_path.exists() and init_path.exists():
                return settings_path
    return None


def _add_djb_to_installed_apps(project_root: Path) -> bool:
    """Add 'djb' to Django's INSTALLED_APPS if not already present.

    Finds the settings.py file and modifies INSTALLED_APPS to include 'djb'.
    Inserts djb after the last django.* app for proper ordering.

    Returns:
        True if djb was added, False if already present or settings not found.
    """
    logger.next("Configuring Django settings")
    settings_path = _find_settings_file(project_root)
    if not settings_path:
        logger.skip("No Django settings.py found")
        return False

    content = settings_path.read_text()

    # Check if djb is already in INSTALLED_APPS
    # Match various formats: "djb", 'djb', with or without trailing comma
    if re.search(r'["\']djb["\']', content):
        logger.done("djb already in INSTALLED_APPS")
        return False

    # Find INSTALLED_APPS list and insert djb
    # Match the pattern: INSTALLED_APPS = [
    pattern = r"(INSTALLED_APPS\s*=\s*\[)"

    match = re.search(pattern, content)
    if not match:
        logger.warning("Could not find INSTALLED_APPS in settings.py")
        return False

    # Find a good insertion point - after the last django.* entry
    # or at the end of the list if no django entries
    lines = content.split("\n")
    installed_apps_start = None
    last_django_line = None
    bracket_depth = 0
    in_installed_apps = False

    for i, line in enumerate(lines):
        if "INSTALLED_APPS" in line and "=" in line:
            installed_apps_start = i
            in_installed_apps = True

        if in_installed_apps:
            bracket_depth += line.count("[") - line.count("]")
            # Match django.* apps (django.contrib.*, django_components, etc.)
            if re.search(r'["\']django[._]', line):
                last_django_line = i
            if bracket_depth == 0 and installed_apps_start is not None and i > installed_apps_start:
                break

    if last_django_line is not None:
        # Insert after the last django.* line
        insert_line = last_django_line
        # Detect indentation from the previous line
        indent_match = re.match(r"^(\s*)", lines[insert_line])
        indent = indent_match.group(1) if indent_match else "    "
        lines.insert(insert_line + 1, f'{indent}"djb",')
    elif installed_apps_start is not None:
        # No django entries, insert after the opening bracket
        indent = "    "
        lines.insert(installed_apps_start + 1, f'{indent}"djb",')
    else:
        logger.warning("Could not determine where to insert djb in INSTALLED_APPS")
        return False

    # Write the modified content
    settings_path.write_text("\n".join(lines))
    logger.done(f"Added djb to INSTALLED_APPS in {settings_path.name}")
    return True


def _update_gitignore_for_project_config(project_root: Path) -> bool:
    """Update .gitignore to ensure .djb/local.yaml is ignored.

    Either:
    - Changes '.djb/' to '.djb/local.yaml' so that project.yaml can be tracked
    - Adds '.djb/local.yaml' if not present

    Returns:
        True if .gitignore was updated, False otherwise.
    """
    gitignore_path = project_root / ".gitignore"
    if not gitignore_path.exists():
        return False

    content = gitignore_path.read_text()

    # Already has the correct entry
    if ".djb/local.yaml" in content:
        return False

    # Check if we need to update (currently ignoring entire .djb/)
    if ".djb/" in content:
        # Replace '.djb/' with '.djb/local.yaml'
        new_content = content.replace(
            "# djb local config (user-specific, not committed)\n.djb/",
            "# djb local config (user-specific, not committed)\n.djb/local.yaml",
        )
        # Fallback: just replace .djb/ if the comment is different
        if new_content == content:
            new_content = content.replace(".djb/", ".djb/local.yaml")

        if new_content != content:
            gitignore_path.write_text(new_content)
            return True
    else:
        # No .djb entry at all - add .djb/local.yaml
        entry = "\n# djb local config (user-specific, not committed)\n.djb/local.yaml\n"
        gitignore_path.write_text(content.rstrip() + entry)
        return True

    return False


def _install_git_hooks(project_root: Path, *, skip: bool = False) -> None:
    """Install git hooks for the project.

    Installs:
    - pre-commit hook to prevent committing pyproject.toml with editable djb

    Args:
        project_root: Path to project root.
        skip: If True, skip hook installation entirely.
    """
    if skip:
        logger.skip("Git hooks installation")
        return

    logger.next("Installing git hooks")

    git_dir = project_root / ".git"
    if not git_dir.exists():
        logger.skip("Not a git repository, skipping hooks")
        return

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    # Source hook script location
    hook_source = project_root / "scripts" / "pre-commit-editable-check"

    if not hook_source.exists():
        logger.warning(f"Hook script not found at {hook_source}")
        logger.info("  Create scripts/pre-commit-editable-check to enable hook installation")
        return

    # Destination hook path
    pre_commit_hook = hooks_dir / "pre-commit"

    # Check if pre-commit hook already exists
    if pre_commit_hook.exists():
        # Check if it's our hook or something else
        content = pre_commit_hook.read_text()
        if "pre-commit-editable-check" in content or "editable djb" in content:
            logger.done("Git hooks already installed")
            return
        else:
            # There's an existing pre-commit hook, don't overwrite it
            logger.warning("Existing pre-commit hook found, not overwriting")
            logger.info(f"  To install manually, add a call to: {hook_source}")
            return

    # Install the hook by copying the script
    shutil.copy(hook_source, pre_commit_hook)
    pre_commit_hook.chmod(0o755)
    logger.done("Git hooks installed (pre-commit: editable djb check)")


# =============================================================================
# Init step functions - each handles one phase of initialization
# =============================================================================


def _init_config(project_root: Path) -> None:
    """Initialize and migrate configuration."""
    config.reload(project_root)

    migration_result = migrate_legacy_config(project_root)
    if migration_result["local"] or migration_result["project"]:
        logger.info("Migrated config from .djb/config.yaml:")
        if migration_result["local"]:
            logger.info(f"  → local.yaml: {', '.join(migration_result['local'])}")
        if migration_result["project"]:
            logger.info(f"  → project.yaml: {', '.join(migration_result['project'])}")
        config.reload(project_root)


def _validate_project(project_root: Path) -> None:
    """Validate we're in a Python project with pyproject.toml."""
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        raise click.ClickException(
            f"No pyproject.toml found in {project_root}. "
            "Run 'djb init' from your project root directory."
        )


def _install_brew_dependencies(*, skip: bool = False) -> None:
    """Install system dependencies via Homebrew.

    Args:
        skip: If True, skip installation entirely.
    """
    is_brew_supported = sys.platform in ("darwin", "linux")

    if skip:
        logger.skip("System dependency installation")
        return

    if not is_brew_supported:
        logger.skip("Homebrew installation (not supported on this platform)")
        logger.info("Please install dependencies manually:")
        logger.info("  - SOPS: https://github.com/getsops/sops")
        logger.info("  - age: https://age-encryption.org/")
        logger.info("  - GnuPG: https://gnupg.org/")
        logger.info("  - PostgreSQL 17: https://www.postgresql.org/")
        logger.info("  - GDAL: https://gdal.org/")
        logger.info("  - Bun: https://bun.sh/")
        return

    logger.next("Installing system dependencies via Homebrew")

    if not check_cmd(["which", "brew"]):
        logger.error("Homebrew not found. Please install from https://brew.sh/")
        raise click.ClickException("Homebrew is required for automatic dependency installation")

    # Install SOPS (for secrets encryption)
    if not check_cmd(["brew", "list", "sops"]):
        run_cmd(["brew", "install", "sops"], label="Installing sops", done_msg="sops installed")
    else:
        logger.done("sops already installed")

    # Install age (for secrets encryption)
    if not check_cmd(["brew", "list", "age"]):
        run_cmd(["brew", "install", "age"], label="Installing age", done_msg="age installed")
    else:
        logger.done("age already installed")

    # Install GnuPG (for age key encryption)
    if not check_cmd(["brew", "list", "gnupg"]):
        run_cmd(
            ["brew", "install", "gnupg"],
            label="Installing gnupg",
            done_msg="gnupg installed",
        )
    else:
        logger.done("gnupg already installed")

    # Install PostgreSQL (for database)
    if not check_cmd(["brew", "list", "postgresql@17"]):
        run_cmd(
            ["brew", "install", "postgresql@17"],
            label="Installing PostgreSQL",
            done_msg="postgresql@17 installed",
        )
    else:
        logger.done("postgresql@17 already installed")

    # Install GDAL (for GeoDjango)
    if not check_cmd(["brew", "list", "gdal"]):
        run_cmd(["brew", "install", "gdal"], label="Installing GDAL", done_msg="gdal installed")
    else:
        logger.done("gdal already installed")

    # Install Bun (JavaScript runtime)
    if not check_cmd(["which", "bun"]):
        run_cmd(
            ["brew", "install", "oven-sh/bun/bun"],
            label="Installing Bun",
            done_msg="bun installed",
        )
    else:
        logger.done("bun already installed")

    logger.done("System dependencies ready")


def _install_python_dependencies(project_root: Path, *, skip: bool = False) -> None:
    """Install Python dependencies via uv.

    Args:
        project_root: Path to project root.
        skip: If True, skip installation entirely.
    """
    if skip:
        logger.skip("Python dependency installation")
        return

    run_cmd(
        ["uv", "sync", "--upgrade-package", "djb"],
        cwd=project_root,
        label="Installing Python dependencies (and upgrading djb to latest)",
        done_msg="Python dependencies installed",
    )


def _install_frontend_dependencies(project_root: Path, *, skip: bool = False) -> None:
    """Install frontend dependencies via bun.

    Args:
        project_root: Path to project root.
        skip: If True, skip installation entirely.
    """
    if skip:
        logger.skip("Frontend dependency installation")
        return

    frontend_dir = project_root / "frontend"
    if frontend_dir.exists():
        run_cmd(
            ["bun", "install"],
            cwd=frontend_dir,
            label="Installing frontend dependencies",
            done_msg="Frontend dependencies installed",
        )
    else:
        logger.skip(f"Frontend directory not found at {frontend_dir}")


def _init_database(project_root: Path, *, skip: bool = False) -> bool:
    """Initialize the development database.

    Args:
        project_root: Path to project root.
        skip: If True, skip database initialization entirely.

    Returns:
        True if database was initialized or skipped, False if failed.
    """
    if skip:
        logger.skip("Database initialization")
        return True

    logger.next("Initializing development database")
    if not init_database(project_root, start_service=True, quiet=False):
        logger.warning("Database initialization failed - you can run 'djb db init' later")
        return False
    return True


def _run_migrations(project_root: Path, *, skip: bool = False) -> bool:
    """Run Django migrations.

    Args:
        project_root: Path to project root.
        skip: If True, skip migrations entirely.

    Returns:
        True if migrations succeeded or skipped, False if failed.
    """
    if skip:
        logger.skip("Django migrations")
        return True

    logger.next("Running Django migrations")
    result = run_cmd(
        ["uv", "run", "python", "manage.py", "migrate"],
        cwd=project_root,
        label="Running migrations",
        done_msg="Migrations complete",
        halt_on_fail=False,
    )
    if result.returncode != 0:
        logger.warning("Migrations failed - you can run 'python manage.py migrate' later")
        return False
    return True


def _run_seed(project_root: Path, *, skip: bool = False) -> bool:
    """Run the host project's seed command if configured.

    Args:
        project_root: Path to project root.
        skip: If True, skip seeding entirely.

    Returns:
        True if seed succeeded, skipped, or not configured, False if failed.
    """
    if skip:
        logger.skip("Database seeding")
        return True

    cfg = get_config(project_root)
    if not cfg.seed_command:
        logger.skip("No seed_command configured")
        return True

    logger.next("Seeding database")
    if not run_seed_command(cfg):
        logger.warning("Seed failed - you can run 'djb seed' later")
        return False
    logger.done("Database seeded")
    return True


def _init_secrets(
    project_root: Path,
    user_email: str | None,
    user_name: str | None,
    project_name: str | None,
    *,
    skip: bool = False,
) -> None:
    """Initialize secrets management.

    Args:
        project_root: Path to project root.
        user_email: User email for secrets.
        user_name: User name for secrets.
        project_name: Project name for secrets.
        skip: If True, skip secrets initialization entirely.
    """
    if skip:
        logger.skip("Secrets initialization")
        return

    logger.next("Initializing secrets management")

    if not ensure_secrets_prerequisites(quiet=True):
        raise click.ClickException("Cannot initialize secrets without SOPS and age")

    if init_gpg_agent_config():
        logger.done("Created GPG agent config with passphrase caching")

    status = init_or_upgrade_secrets(
        project_root, email=user_email, name=user_name, project_name=project_name
    )

    if status.initialized:
        logger.done(f"Created secrets: {', '.join(status.initialized)}")
    if status.upgraded:
        logger.done(f"Upgraded secrets: {', '.join(status.upgraded)}")
    if status.up_to_date and not status.initialized and not status.upgraded:
        logger.done("Secrets already up to date")

    # Auto-commit .sops.yaml if this is a git repo and the file was modified
    _auto_commit_secrets(project_root, user_email)


def _auto_commit_secrets(project_root: Path, user_email: str | None) -> None:
    """Auto-commit secrets config to git if modified."""
    secrets_dir = project_root / "secrets"
    git_dir = project_root / ".git"

    if not git_dir.exists() or not user_email:
        return

    sops_config = secrets_dir / ".sops.yaml"
    files_to_commit = []

    if sops_config.exists():
        result = run_cmd(
            ["git", "status", "--porcelain", str(sops_config)],
            cwd=project_root,
            halt_on_fail=False,
        )
        if result.stdout.strip():
            files_to_commit.append(str(sops_config.relative_to(project_root)))

    if files_to_commit:
        logger.next("Committing public key to git")
        logger.info(f"Files: {', '.join(files_to_commit)}")

        for file in files_to_commit:
            run_cmd(["git", "add", file], cwd=project_root, halt_on_fail=False)

        commit_msg = f"Add public key for {user_email}"
        result = run_cmd(
            ["git", "commit", "-m", commit_msg],
            cwd=project_root,
            halt_on_fail=False,
            fail_msg="Could not commit public key",
        )
        if result.returncode == 0:
            if result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    logger.info(f"  {line}")
            logger.done("Public key committed")


def _auto_commit_project_config(project_root: Path, gitignore_updated: bool) -> None:
    """Auto-commit project config files to git if modified."""
    git_dir = project_root / ".git"
    if not git_dir.exists():
        return

    project_config_path = get_config_path(PROJECT, project_root)
    gitignore_path = project_root / ".gitignore"

    config_files_to_commit = []

    if project_config_path.exists():
        result = run_cmd(
            ["git", "status", "--porcelain", str(project_config_path)],
            cwd=project_root,
            halt_on_fail=False,
        )
        if result.stdout.strip():
            config_files_to_commit.append(str(project_config_path.relative_to(project_root)))

    if gitignore_updated:
        result = run_cmd(
            ["git", "status", "--porcelain", str(gitignore_path)],
            cwd=project_root,
            halt_on_fail=False,
        )
        if result.stdout.strip():
            config_files_to_commit.append(".gitignore")

    if config_files_to_commit:
        logger.next("Committing project config to git")
        logger.info(f"Files: {', '.join(config_files_to_commit)}")

        for file in config_files_to_commit:
            run_cmd(["git", "add", file], cwd=project_root, halt_on_fail=False)

        commit_msg = "Add djb project config"
        result = run_cmd(
            ["git", "commit", "-m", commit_msg],
            cwd=project_root,
            halt_on_fail=False,
            fail_msg="Could not commit project config",
        )
        if result.returncode == 0:
            if result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    logger.info(f"  {line}")
            logger.done("Project config committed")


def _show_success_message() -> None:
    """Show final success message with next steps."""
    logger.done("djb initialization complete!")
    logger.note()
    logger.info("To start developing, run in separate terminals:")
    logger.info("  1. python manage.py runserver")
    logger.info("  2. cd frontend && bun run dev")
    logger.note()
    clip_cmd = _get_clipboard_command()
    logger.tip(f"Back up your private secrets Age key: djb secrets export-key | {clip_cmd}")
    logger.tip(
        "Push your commit, then ask a teammate to run: djb secrets rotate\n"
        "         (This gives you access to staging/production secrets)"
    )


@click.command("init")
@click.option(
    "--skip-brew",
    is_flag=True,
    help="Skip installing system dependencies via Homebrew",
)
@click.option(
    "--skip-python",
    is_flag=True,
    help="Skip installing Python dependencies",
)
@click.option(
    "--skip-frontend",
    is_flag=True,
    help="Skip installing frontend dependencies",
)
@click.option(
    "--skip-db",
    is_flag=True,
    help="Skip database initialization",
)
@click.option(
    "--skip-migrations",
    is_flag=True,
    help="Skip running Django migrations",
)
@click.option(
    "--skip-seed",
    is_flag=True,
    help="Skip running the seed command",
)
@click.option(
    "--skip-secrets",
    is_flag=True,
    help="Skip secrets initialization",
)
@click.option(
    "--skip-hooks",
    is_flag=True,
    help="Skip installing git hooks",
)
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Project root directory (default: current directory)",
)
def init(
    skip_brew: bool,
    skip_python: bool,
    skip_frontend: bool,
    skip_db: bool,
    skip_migrations: bool,
    skip_seed: bool,
    skip_secrets: bool,
    skip_hooks: bool,
    project_root: Path | None,
):
    """Initialize djb development environment.

    Sets up everything needed for local development:

    \b
    * System dependencies (Homebrew): SOPS, age, PostgreSQL, GDAL, Bun
    * Python dependencies: uv sync
    * Django settings: adds djb to INSTALLED_APPS
    * Frontend dependencies: bun install in frontend/
    * Database: creates PostgreSQL database and user
    * Django migrations: runs migrate command
    * Database seeding: runs seed command (if configured)
    * Git hooks: pre-commit hook to prevent committing editable djb
    * Secrets management: SOPS-encrypted configuration

    This command is idempotent - safe to run multiple times.
    Already-installed dependencies are skipped automatically.

    \b
    Examples:
      djb init                    # Full setup
      djb init --skip-brew        # Skip Homebrew (already installed)
      djb init --skip-db          # Skip database (configure later)
      djb init --skip-secrets     # Skip secrets (configure later)
    """
    if project_root is None:
        project_root = Path.cwd()

    _init_config(project_root)
    _validate_project(project_root)

    logger.info("Initializing djb development environment")

    user_name, user_email = _configure_user_identity()
    project_name = _configure_project_name(project_root)
    _configure_hostname(project_name)

    gitignore_updated = _update_gitignore_for_project_config(project_root)
    if gitignore_updated:
        logger.done("Added .djb/local.yaml to .gitignore")

    _install_brew_dependencies(skip=skip_brew)
    _install_python_dependencies(project_root, skip=skip_python)
    _add_djb_to_installed_apps(project_root)
    _install_frontend_dependencies(project_root, skip=skip_frontend)
    _init_database(project_root, skip=skip_db)
    _run_migrations(project_root, skip=skip_migrations)
    _run_seed(project_root, skip=skip_seed)
    _install_git_hooks(project_root, skip=skip_hooks)
    _init_secrets(project_root, user_email, user_name, project_name, skip=skip_secrets)
    _auto_commit_project_config(project_root, gitignore_updated)
    _show_success_message()
