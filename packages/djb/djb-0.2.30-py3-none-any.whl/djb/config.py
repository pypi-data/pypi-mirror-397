"""
djb configuration - Unified configuration system for djb CLI.

Configuration is loaded with the following priority (highest to lowest):
1. CLI flags (applied via with_overrides())
2. Environment variables (DJB_ prefix)
3. Local config (.djb/local.yaml) - user-specific, gitignored
4. Project config (.djb/project.yaml) - shared, committed
5. Default values

Two config files are used:
- .djb/local.yaml: User-specific settings (name, email, mode) - NOT committed
- .djb/project.yaml: Project settings (hostname, project_name, target) - committed

Local config can override any project setting for user experimentation.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

import yaml

from djb.project import find_project_root
from djb.types import Mode, Target

__all__ = [
    # Main API
    "DjbConfig",
    "get_config",
    # Config file access (Django settings-style)
    "config",
    # Low-level helpers
    "get_config_dir",
    "get_config_path",
    "load_config",
    "save_config",
    "load_merged_config",
    "get_project_name_from_pyproject",
    "migrate_legacy_config",
    # Config type constants
    "LOCAL",
    "PROJECT",
]

# Config type constants
LOCAL = "local"
PROJECT = "project"

# Config file names (internal)
_CONFIG_FILES = {
    LOCAL: "local.yaml",
    PROJECT: "project.yaml",
}
_LEGACY_CONFIG_FILE = "config.yaml"  # For migration

# Settings that only make sense per-user (never saved to project config)
USER_ONLY_KEYS = ("name", "email", "mode")

# Simple string config keys that follow the "env > file" priority pattern
STRING_CONFIG_KEYS = ("name", "email", "hostname", "seed_command")


def get_config_dir(project_root: Path | None = None) -> Path:
    """Get the djb configuration directory (.djb/ in project root).

    Args:
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        Path to .djb/ directory in the project.
    """
    if project_root is None:
        project_root = find_project_root(fallback_to_cwd=True)
    return project_root / ".djb"


def get_config_path(config_type: str, project_root: Path | None = None) -> Path:
    """Get path to a config file by type.

    Args:
        config_type: Config type (LOCAL or PROJECT).
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        Path to the config file.
    """
    if config_type not in _CONFIG_FILES:
        raise ValueError(f"Unknown config type: {config_type}")
    return get_config_dir(project_root) / _CONFIG_FILES[config_type]


def load_config(config_type: str, project_root: Path | None = None) -> dict[str, Any]:
    """Load a configuration file by type.

    Args:
        config_type: Config type (LOCAL or PROJECT).
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        Configuration dict, or empty dict if the file doesn't exist.
    """
    path = get_config_path(config_type, project_root)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data if data else {}


def save_config(config_type: str, data: dict[str, Any], project_root: Path | None = None) -> None:
    """Save a configuration file by type.

    Args:
        config_type: Config type (LOCAL or PROJECT).
        data: Configuration dict to save.
        project_root: Project root path. Defaults to auto-detected project root.
    """
    path = get_config_path(config_type, project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def load_merged_config(project_root: Path | None = None) -> dict[str, Any]:
    """Load merged configuration (project config + local overrides).

    This loads both config files and merges them, with local config
    taking precedence over project config.

    Args:
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        Merged configuration dict.
    """
    project_config = load_config(PROJECT, project_root)
    local_config = load_config(LOCAL, project_root)

    # Merge: local overrides project
    return {**project_config, **local_config}


def migrate_legacy_config(project_root: Path | None = None) -> dict[str, list[str]]:
    """Migrate from legacy config.yaml to local.yaml + project.yaml.

    If .djb/config.yaml exists:
    1. Move user-only keys to .djb/local.yaml
    2. Move project keys to .djb/project.yaml
    3. Delete the old config.yaml

    Args:
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        Dict with 'local' and 'project' keys listing migrated settings.
    """
    config_dir = get_config_dir(project_root)
    legacy_path = config_dir / _LEGACY_CONFIG_FILE

    result: dict[str, list[str]] = {"local": [], "project": []}

    if not legacy_path.exists():
        return result

    # Load legacy config
    with open(legacy_path, "r", encoding="utf-8") as f:
        legacy_config = yaml.safe_load(f)
    if not legacy_config:
        # Empty file, just remove it
        legacy_path.unlink()
        return result

    # Load existing configs (may already have some values)
    local_config = load_config(LOCAL, project_root)
    project_config = load_config(PROJECT, project_root)

    # Migrate each key
    for key, value in legacy_config.items():
        if key in USER_ONLY_KEYS:
            # User-only → local config
            if key not in local_config:
                local_config[key] = value
                result["local"].append(key)
        else:
            # Everything else → project config
            if key not in project_config:
                project_config[key] = value
                result["project"].append(key)

    # Save migrated configs
    if local_config:
        save_config(LOCAL, local_config, project_root)
    if project_config:
        save_config(PROJECT, project_config, project_root)

    # Remove legacy config
    legacy_path.unlink()

    return result


def get_project_name_from_pyproject(project_root: Path | None = None) -> str | None:
    """Read the project name from pyproject.toml.

    Args:
        project_root: Project root path. Defaults to auto-detected project root.

    Returns:
        Project name from pyproject.toml, or None if not found.
    """
    if project_root is None:
        project_root = find_project_root(fallback_to_cwd=True)

    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        return None

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data.get("project", {}).get("name")
    except (tomllib.TOMLDecodeError, OSError):
        return None


def _get_env_value(key: str) -> str | None:
    """Get an environment variable with DJB_ prefix."""
    return os.getenv(f"DJB_{key.upper()}")


@dataclass
class DjbConfig:
    """Unified configuration for djb CLI.

    Loads configuration from multiple sources with priority:
    1. CLI flags (via with_overrides())
    2. Environment variables (DJB_ prefix)
    3. Config file (.djb/config.yaml)
    4. Defaults (including pyproject.toml for project_name)
    """

    # The four globals - all set by get_config() before use.
    project_dir: Path = field(default=None)  # type: ignore[assignment]
    project_name: str = field(default=None)  # type: ignore[assignment]
    mode: Mode = Mode.DEVELOPMENT
    target: Target = Target.HEROKU

    # User identity - set by get_config() from config file or env vars.
    name: str = field(default=None)  # type: ignore[assignment]
    email: str = field(default=None)  # type: ignore[assignment]

    # Deployment hostname (e.g., "myapp.com") - set by get_config() from config file or env vars.
    hostname: str = field(default=None)  # type: ignore[assignment]

    # Seed command (e.g., "myapp.cli.seed:seed") - module:attr path to a Click command
    seed_command: str = field(default=None)  # type: ignore[assignment]

    # Internal: tracks which fields were explicitly set via CLI
    _cli_overrides: dict[str, Any] = field(default_factory=dict, repr=False)

    def with_overrides(self, **kwargs: Any) -> "DjbConfig":
        """Create a new config with CLI overrides applied.

        Args:
            **kwargs: Override values from CLI flags.

        Returns:
            New DjbConfig with overrides applied.
        """
        # Filter out None values (keep only explicit overrides)
        cli_overrides = {k: v for k, v in kwargs.items() if v is not None}

        # Use dataclasses.replace() to create new config with overrides
        new_config = replace(self, **cli_overrides, _cli_overrides=cli_overrides)
        return new_config

    def save(self, project_root: Path | None = None) -> None:
        """Save current configuration to appropriate config files.

        User-only settings go to .djb/local.yaml.
        Project settings go to .djb/project.yaml.

        Args:
            project_root: Project root path. Defaults to self.project_dir.
        """
        if project_root is None:
            project_root = self.project_dir

        # Load existing configs to preserve unknown fields
        local_config = load_config(LOCAL, project_root)
        project_config = load_config(PROJECT, project_root)

        # User-only settings go to local config
        local_config["name"] = self.name
        local_config["email"] = self.email
        local_config["mode"] = str(self.mode)

        # Project settings go to project config
        project_config["project_name"] = self.project_name
        project_config["target"] = str(self.target)
        if self.hostname:
            project_config["hostname"] = self.hostname

        # Remove None values
        local_config = {k: v for k, v in local_config.items() if v is not None}
        project_config = {k: v for k, v in project_config.items() if v is not None}

        save_config(LOCAL, local_config, project_root)
        save_config(PROJECT, project_config, project_root)

    def save_mode(self, project_root: Path | None = None) -> None:
        """Save only the mode to local config file.

        Used when --mode is explicitly passed to persist it.

        Args:
            project_root: Project root path. Defaults to self.project_dir.
        """
        if project_root is None:
            project_root = self.project_dir

        existing = load_config(LOCAL, project_root)
        existing["mode"] = str(self.mode)
        save_config(LOCAL, existing, project_root)


def get_config(project_root: Path | None = None) -> DjbConfig:
    """Get the djb configuration.

    This is the main entry point for loading configuration.
    Loads from (highest to lowest priority):
    1. Environment variables (DJB_ prefix)
    2. Local config (.djb/local.yaml)
    3. Project config (.djb/project.yaml)
    4. Default values

    Args:
        project_root: Project root path. Defaults to auto-detected.

    Returns:
        DjbConfig instance with all sources merged.
    """
    # Start with defaults
    config_values: dict[str, Any] = {}

    # Load from config file (lowest priority after defaults)
    file_config = load_merged_config(project_root)

    # project_dir: env > file > default (cwd)
    if env_val := _get_env_value("PROJECT_DIR"):
        config_values["project_dir"] = Path(env_val)
    elif "project_dir" in file_config:
        config_values["project_dir"] = Path(file_config["project_dir"])
    else:
        config_values["project_dir"] = project_root or find_project_root(fallback_to_cwd=True)

    # project_name: env > file > pyproject.toml
    if env_val := _get_env_value("PROJECT_NAME"):
        config_values["project_name"] = env_val
    elif "project_name" in file_config:
        config_values["project_name"] = file_config["project_name"]
    else:
        config_values["project_name"] = get_project_name_from_pyproject(
            config_values.get("project_dir")
        )

    # mode: env > file > default
    config_values["mode"] = (
        Mode.parse(_get_env_value("MODE"))
        or Mode.parse(file_config.get("mode"))
        or Mode.DEVELOPMENT
    )

    # target: env > file > default
    config_values["target"] = (
        Target.parse(_get_env_value("TARGET"))
        or Target.parse(file_config.get("target"))
        or Target.HEROKU
    )

    # String configs: env > file
    for key in STRING_CONFIG_KEYS:
        config_values[key] = _get_env_value(key) or file_config.get(key)

    return DjbConfig(**config_values)


# ============================================================================
# Django settings-style config access
# ============================================================================


class _LazyConfig:
    """Lazy config file accessor (Django settings-style).

    Usage:
        from djb.config import config

        # Read values (merged from project + local config)
        name = config.name
        email = config.email

        # Write values (auto-saves to appropriate file)
        config.name = "John Doe"      # → local.yaml (user-only)
        config.hostname = "app.com"   # → project.yaml (project setting)

        # Delete values (removes from config file)
        del config.seed_command       # → removes from project.yaml

        # Check if a key is set
        if 'seed_command' in config:
            ...

        # Reload from disk
        config.reload()
    """

    _KEYS = ("name", "email", "hostname", "project_name", "mode", "target", "seed_command")

    def __init__(self) -> None:
        object.__setattr__(self, "_data", None)
        object.__setattr__(self, "_project_root", None)

    def _ensure_loaded(self) -> dict[str, Any]:
        """Load config from disk if not already loaded."""
        if self._data is None:
            project_root = find_project_root(fallback_to_cwd=True)
            object.__setattr__(self, "_project_root", project_root)
            object.__setattr__(self, "_data", load_merged_config(project_root))
        return self._data

    def reload(self, project_root: Path | None = None) -> None:
        """Reload config from disk, optionally from a different project root."""
        if project_root is not None:
            object.__setattr__(self, "_project_root", project_root)
        object.__setattr__(self, "_data", load_merged_config(self._project_root))

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            return object.__getattribute__(self, name)
        data = self._ensure_loaded()
        # Special case: project_name falls back to pyproject.toml
        if name == "project_name" and "project_name" not in data:
            return get_project_name_from_pyproject(self._project_root)
        return data.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return

        # Update in-memory cache
        data = self._ensure_loaded()
        data[name] = value

        # Route to appropriate config file
        config_type = LOCAL if name in USER_ONLY_KEYS else PROJECT
        existing = load_config(config_type, self._project_root)
        existing[name] = value
        save_config(config_type, existing, self._project_root)

    def __delattr__(self, name: str) -> None:
        if name.startswith("_"):
            object.__delattr__(self, name)
            return

        # Remove from in-memory cache
        data = self._ensure_loaded()
        data.pop(name, None)

        # Remove from appropriate config file
        config_type = LOCAL if name in USER_ONLY_KEYS else PROJECT
        existing = load_config(config_type, self._project_root)
        if name in existing:
            del existing[name]
            save_config(config_type, existing, self._project_root)

    def __contains__(self, name: str) -> bool:
        """Check if a config key is set."""
        data = self._ensure_loaded()
        return name in data


# Module-level singleton
config = _LazyConfig()
