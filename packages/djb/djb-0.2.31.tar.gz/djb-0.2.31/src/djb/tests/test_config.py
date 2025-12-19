"""Tests for djb.config module."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from djb.config import (
    LOCAL,
    PROJECT,
    DjbConfig,
    config,
    get_config,
    get_config_dir,
    get_config_path,
    get_project_name_from_pyproject,
    load_config,
    load_merged_config,
    migrate_legacy_config,
    save_config,
)
from djb.types import Mode, Target


class TestConfigPaths:
    """Tests for config path helpers."""

    def test_get_config_dir(self, tmp_path):
        """Test get_config_dir returns .djb directory."""
        result = get_config_dir(tmp_path)
        assert result == tmp_path / ".djb"

    def test_get_config_path_local(self, tmp_path):
        """Test get_config_path returns local.yaml path for LOCAL type."""
        result = get_config_path(LOCAL, tmp_path)
        assert result == tmp_path / ".djb" / "local.yaml"

    def test_get_config_path_project(self, tmp_path):
        """Test get_config_path returns project.yaml path for PROJECT type."""
        result = get_config_path(PROJECT, tmp_path)
        assert result == tmp_path / ".djb" / "project.yaml"

    def test_get_config_path_invalid_type(self, tmp_path):
        """Test get_config_path raises error for invalid config type."""
        with pytest.raises(ValueError, match="Unknown config type"):
            get_config_path("invalid", tmp_path)


class TestLoadSaveConfig:
    """Tests for load_config and save_config."""

    def test_load_config_missing(self, tmp_path):
        """Test loading when config file doesn't exist."""
        result = load_config(LOCAL, tmp_path)
        assert result == {}

    def test_load_config_exists(self, tmp_path):
        """Test loading existing config file."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "local.yaml"
        config_file.write_text("name: John\nemail: john@example.com\n")

        result = load_config(LOCAL, tmp_path)
        assert result == {"name": "John", "email": "john@example.com"}

    def test_load_config_empty(self, tmp_path):
        """Test loading empty config file."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "local.yaml"
        config_file.write_text("")

        result = load_config(LOCAL, tmp_path)
        assert result == {}

    def test_save_config_creates_directory(self, tmp_path):
        """Test save_config creates .djb directory if needed."""
        data = {"name": "John"}
        save_config(LOCAL, data, tmp_path)

        assert (tmp_path / ".djb").exists()
        assert (tmp_path / ".djb" / "local.yaml").exists()

    def test_save_config_content(self, tmp_path):
        """Test save_config writes correct content."""
        data = {"name": "John", "email": "john@example.com"}
        save_config(LOCAL, data, tmp_path)

        result = load_config(LOCAL, tmp_path)
        assert result == data

    def test_load_merged_config_missing(self, tmp_path):
        """Test loading merged config when files don't exist."""
        result = load_merged_config(tmp_path)
        assert result == {}

    def test_load_merged_config_merges_both(self, tmp_path):
        """Test load_merged_config merges project + local configs."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()

        # Project config
        (config_dir / "project.yaml").write_text("hostname: example.com\ntarget: heroku\n")
        # Local config
        (config_dir / "local.yaml").write_text("name: John\nemail: john@example.com\n")

        result = load_merged_config(tmp_path)
        assert result == {
            "hostname": "example.com",
            "target": "heroku",
            "name": "John",
            "email": "john@example.com",
        }

    def test_local_config_overrides_project_config(self, tmp_path):
        """Test local config takes precedence over project config."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()

        # Project config sets target to heroku
        (config_dir / "project.yaml").write_text("target: heroku\nhostname: example.com\n")
        # Local config overrides target to docker
        (config_dir / "local.yaml").write_text("target: docker\n")

        result = load_merged_config(tmp_path)
        assert result["target"] == "docker"
        assert result["hostname"] == "example.com"


class TestGetProjectNameFromPyproject:
    """Tests for get_project_name_from_pyproject."""

    def test_reads_project_name(self, tmp_path):
        """Test reading project name from pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\nversion = "1.0.0"\n')

        result = get_project_name_from_pyproject(tmp_path)
        assert result == "myproject"

    def test_missing_pyproject(self, tmp_path):
        """Test when pyproject.toml doesn't exist."""
        result = get_project_name_from_pyproject(tmp_path)
        assert result is None

    def test_missing_project_section(self, tmp_path):
        """Test when pyproject.toml has no project section."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.pytest]\n")

        result = get_project_name_from_pyproject(tmp_path)
        assert result is None

    def test_missing_name_field(self, tmp_path):
        """Test when project section has no name."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.0.0"\n')

        result = get_project_name_from_pyproject(tmp_path)
        assert result is None

    def test_invalid_toml(self, tmp_path):
        """Test with invalid TOML content."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("this is not valid toml [[[")

        result = get_project_name_from_pyproject(tmp_path)
        assert result is None


class TestDjbConfig:
    """Tests for DjbConfig class."""

    def test_default_values(self):
        """Test DjbConfig default values."""
        config = DjbConfig()
        assert config.project_dir is None
        assert config.project_name is None
        assert config.mode == Mode.DEVELOPMENT
        assert config.target == Target.HEROKU
        assert config.name is None
        assert config.email is None

    def test_with_overrides(self):
        """Test with_overrides creates new config with values."""
        config = DjbConfig()
        new_config = config.with_overrides(
            name="John",
            email="john@example.com",
            mode=Mode.PRODUCTION,
        )

        # Original unchanged
        assert config.name is None
        assert config.mode == Mode.DEVELOPMENT

        # New config has overrides
        assert new_config.name == "John"
        assert new_config.email == "john@example.com"
        assert new_config.mode == Mode.PRODUCTION

    def test_with_overrides_ignores_none(self):
        """Test with_overrides ignores None values."""
        config = DjbConfig(name="John")
        new_config = config.with_overrides(name=None, email="john@example.com")

        # name should be preserved since override was None
        assert new_config.name == "John"
        assert new_config.email == "john@example.com"

    def test_with_overrides_tracks_cli_overrides(self):
        """Test with_overrides tracks which fields were set."""
        config = DjbConfig()
        new_config = config.with_overrides(mode=Mode.STAGING, name="John")

        assert new_config._cli_overrides == {"mode": Mode.STAGING, "name": "John"}

    def test_save(self, tmp_path):
        """Test save persists config to file."""
        cfg = DjbConfig(
            project_dir=tmp_path,
            project_name="myproject",
            name="John",
            email="john@example.com",
            mode=Mode.STAGING,
            target=Target.HEROKU,
        )
        cfg.save()

        # User settings go to local config
        local = load_config(LOCAL, tmp_path)
        assert local["name"] == "John"
        assert local["email"] == "john@example.com"
        assert local["mode"] == "staging"

        # Project settings go to project config
        project = load_config(PROJECT, tmp_path)
        assert project["project_name"] == "myproject"
        assert project["target"] == "heroku"

    def test_save_removes_none_values(self, tmp_path):
        """Test save doesn't write None values."""
        # Note: email is typed as str but defaults to None at runtime.
        # This tests that None values aren't persisted to the config file.
        cfg = DjbConfig(project_dir=tmp_path, name="John")
        cfg.save()

        loaded = load_config(LOCAL, tmp_path)
        assert loaded["name"] == "John"
        assert "email" not in loaded

    def test_save_mode(self, tmp_path):
        """Test save_mode only saves mode."""
        # Create existing config
        save_config(LOCAL, {"name": "John", "mode": "development"}, tmp_path)

        cfg = DjbConfig(project_dir=tmp_path, mode=Mode.PRODUCTION)
        cfg.save_mode()

        loaded = load_config(LOCAL, tmp_path)
        assert loaded["mode"] == "production"
        assert loaded["name"] == "John"  # Preserved


class TestGetConfig:
    """Tests for get_config function."""

    def test_loads_from_file(self, tmp_path):
        """Test get_config loads from config file."""
        save_config(
            LOCAL, {"name": "John", "email": "john@example.com", "mode": "staging"}, tmp_path
        )

        cfg = get_config(tmp_path)
        assert cfg.name == "John"
        assert cfg.email == "john@example.com"
        assert cfg.mode == Mode.STAGING

    def test_env_overrides_file(self, tmp_path):
        """Test environment variables override file config."""
        save_config(LOCAL, {"name": "John"}, tmp_path)

        with patch.dict(os.environ, {"DJB_NAME": "Jane"}):
            cfg = get_config(tmp_path)
            assert cfg.name == "Jane"

    def test_project_name_from_pyproject(self, tmp_path):
        """Test project_name falls back to pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "myproject"\n')

        cfg = get_config(tmp_path)
        assert cfg.project_name == "myproject"

    def test_project_name_config_overrides_pyproject(self, tmp_path):
        """Test config file project_name overrides pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "pyproject-name"\n')
        save_config(PROJECT, {"project_name": "config-name"}, tmp_path)

        cfg = get_config(tmp_path)
        assert cfg.project_name == "config-name"

    def test_default_mode(self, tmp_path):
        """Test default mode is DEVELOPMENT."""
        cfg = get_config(tmp_path)
        assert cfg.mode == Mode.DEVELOPMENT

    def test_default_target(self, tmp_path):
        """Test default target is HEROKU."""
        cfg = get_config(tmp_path)
        assert cfg.target == Target.HEROKU

    def test_env_mode(self, tmp_path):
        """Test DJB_MODE environment variable."""
        with patch.dict(os.environ, {"DJB_MODE": "production"}):
            cfg = get_config(tmp_path)
            assert cfg.mode == Mode.PRODUCTION

    def test_env_target(self, tmp_path):
        """Test DJB_TARGET environment variable."""
        with patch.dict(os.environ, {"DJB_TARGET": "heroku"}):
            cfg = get_config(tmp_path)
            assert cfg.target == Target.HEROKU

    def test_project_dir_defaults_to_passed_root(self, tmp_path):
        """Test project_dir defaults to the passed project_root."""
        cfg = get_config(tmp_path)
        assert cfg.project_dir == tmp_path

    def test_invalid_mode_falls_back_to_default(self, tmp_path):
        """Test that invalid mode in file falls back to development."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "local.yaml"
        config_file.write_text("mode: invalid_mode\n")

        cfg = get_config(tmp_path)

        assert cfg.mode == Mode.DEVELOPMENT

    def test_invalid_target_falls_back_to_default(self, tmp_path):
        """Test that invalid target in file falls back to heroku."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "local.yaml"
        config_file.write_text("target: invalid_target\n")

        cfg = get_config(tmp_path)

        assert cfg.target == Target.HEROKU


class TestConfigPriority:
    """Tests for configuration priority (CLI > env > file > default)."""

    def test_cli_overrides_env(self, tmp_path):
        """Test that CLI overrides take precedence over env vars."""
        with patch.dict(os.environ, {"DJB_MODE": "staging"}):
            config = get_config(tmp_path)
            config = config.with_overrides(mode=Mode.PRODUCTION)

            assert config.mode == Mode.PRODUCTION


class TestConfigSingleton:
    """Tests for the config singleton."""

    def test_get_name(self, tmp_path):
        """Test config.name returns configured name."""
        save_config(LOCAL, {"name": "John"}, tmp_path)
        config.reload(tmp_path)
        assert config.name == "John"

    def test_get_name_missing(self, tmp_path):
        """Test config.name returns None when not configured."""
        config.reload(tmp_path)
        assert config.name is None

    def test_set_name(self, tmp_path):
        """Test setting config.name saves to config."""
        config.reload(tmp_path)
        config.name = "John"
        assert config.name == "John"
        # Verify persisted to local config (user setting)
        assert load_config(LOCAL, tmp_path)["name"] == "John"

    def test_get_email(self, tmp_path):
        """Test config.email returns configured email."""
        save_config(LOCAL, {"email": "john@example.com"}, tmp_path)
        config.reload(tmp_path)
        assert config.email == "john@example.com"

    def test_get_email_missing(self, tmp_path):
        """Test config.email returns None when not configured."""
        config.reload(tmp_path)
        assert config.email is None

    def test_set_email(self, tmp_path):
        """Test setting config.email saves to config."""
        config.reload(tmp_path)
        config.email = "john@example.com"
        assert config.email == "john@example.com"
        # Verify persisted to local config (user setting)
        assert load_config(LOCAL, tmp_path)["email"] == "john@example.com"

    def test_get_project_name_from_config(self, tmp_path):
        """Test config.project_name returns from config."""
        save_config(PROJECT, {"project_name": "myproject"}, tmp_path)
        config.reload(tmp_path)
        assert config.project_name == "myproject"

    def test_get_project_name_from_pyproject(self, tmp_path):
        """Test config.project_name falls back to pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "pyproject-name"\n')
        config.reload(tmp_path)

        assert config.project_name == "pyproject-name"

    def test_get_project_name_config_overrides_pyproject(self, tmp_path):
        """Test config.project_name prefers config over pyproject."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "pyproject-name"\n')
        save_config(PROJECT, {"project_name": "config-name"}, tmp_path)
        config.reload(tmp_path)

        assert config.project_name == "config-name"

    def test_set_project_name(self, tmp_path):
        """Test setting config.project_name saves to config."""
        config.reload(tmp_path)
        config.project_name = "myproject"
        assert config.project_name == "myproject"
        # Verify persisted to project config (project setting)
        assert load_config(PROJECT, tmp_path)["project_name"] == "myproject"

    def test_setattr_preserves_other_config(self, tmp_path):
        """Test setting one attribute preserves other config values."""
        save_config(LOCAL, {"name": "John", "email": "john@example.com"}, tmp_path)
        config.reload(tmp_path)

        config.project_name = "myproject"

        # User settings should still be in local config
        local = load_config(LOCAL, tmp_path)
        assert local["name"] == "John"
        assert local["email"] == "john@example.com"
        # Project setting should be in project config
        project = load_config(PROJECT, tmp_path)
        assert project["project_name"] == "myproject"


class TestDualSourceConfig:
    """Tests for dual-source configuration (project.yaml + local.yaml)."""

    def test_load_project_config_missing(self, tmp_path):
        """Test loading when project config file doesn't exist."""
        result = load_config(PROJECT, tmp_path)
        assert result == {}

    def test_load_project_config_exists(self, tmp_path):
        """Test loading existing project config file."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        config_file = config_dir / "project.yaml"
        config_file.write_text("hostname: example.com\nproject_name: myproject\n")

        result = load_config(PROJECT, tmp_path)
        assert result == {"hostname": "example.com", "project_name": "myproject"}

    def test_save_project_config(self, tmp_path):
        """Test saving project config file."""
        save_config(PROJECT, {"hostname": "example.com"}, tmp_path)

        result = load_config(PROJECT, tmp_path)
        assert result == {"hostname": "example.com"}

    def test_singleton_routes_user_settings_to_local(self, tmp_path):
        """Test setting user-only settings saves to local.yaml."""
        config.reload(tmp_path)
        config.name = "John"
        config.email = "john@example.com"

        # Should be in local config
        assert load_config(LOCAL, tmp_path)["name"] == "John"
        assert load_config(LOCAL, tmp_path)["email"] == "john@example.com"
        # Should NOT be in project config
        assert "name" not in load_config(PROJECT, tmp_path)
        assert "email" not in load_config(PROJECT, tmp_path)

    def test_singleton_routes_project_settings_to_project(self, tmp_path):
        """Test setting project settings saves to project.yaml."""
        config.reload(tmp_path)
        config.hostname = "example.com"
        config.project_name = "myproject"

        # Should be in project config
        assert load_config(PROJECT, tmp_path)["hostname"] == "example.com"
        assert load_config(PROJECT, tmp_path)["project_name"] == "myproject"
        # Should NOT be in local config
        assert "hostname" not in load_config(LOCAL, tmp_path)
        assert "project_name" not in load_config(LOCAL, tmp_path)


class TestMigrateLegacyConfig:
    """Tests for migrate_legacy_config function."""

    def test_no_legacy_config(self, tmp_path):
        """Test migration when no legacy config exists."""
        result = migrate_legacy_config(tmp_path)
        assert result == {"local": [], "project": []}

    def test_empty_legacy_config(self, tmp_path):
        """Test migration removes empty legacy config."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        legacy_file = config_dir / "config.yaml"
        legacy_file.write_text("")

        result = migrate_legacy_config(tmp_path)

        assert result == {"local": [], "project": []}
        assert not legacy_file.exists()

    def test_migrates_user_settings_to_local(self, tmp_path):
        """Test migration moves user settings to local.yaml."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        legacy_file = config_dir / "config.yaml"
        legacy_file.write_text("name: John\nemail: john@example.com\nmode: staging\n")

        result = migrate_legacy_config(tmp_path)

        assert set(result["local"]) == {"name", "email", "mode"}
        assert result["project"] == []
        assert not legacy_file.exists()

        local = load_config(LOCAL, tmp_path)
        assert local["name"] == "John"
        assert local["email"] == "john@example.com"
        assert local["mode"] == "staging"

    def test_migrates_project_settings_to_project(self, tmp_path):
        """Test migration moves project settings to project.yaml."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        legacy_file = config_dir / "config.yaml"
        legacy_file.write_text("hostname: example.com\nproject_name: myproject\ntarget: heroku\n")

        result = migrate_legacy_config(tmp_path)

        assert result["local"] == []
        assert set(result["project"]) == {"hostname", "project_name", "target"}
        assert not legacy_file.exists()

        project = load_config(PROJECT, tmp_path)
        assert project["hostname"] == "example.com"
        assert project["project_name"] == "myproject"
        assert project["target"] == "heroku"

    def test_migrates_mixed_settings(self, tmp_path):
        """Test migration splits mixed settings correctly."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()
        legacy_file = config_dir / "config.yaml"
        legacy_file.write_text(
            "name: John\nemail: john@example.com\nhostname: example.com\nproject_name: myproject\n"
        )

        result = migrate_legacy_config(tmp_path)

        assert set(result["local"]) == {"name", "email"}
        assert set(result["project"]) == {"hostname", "project_name"}
        assert not legacy_file.exists()

    def test_preserves_existing_config_values(self, tmp_path):
        """Test migration doesn't overwrite existing values."""
        config_dir = tmp_path / ".djb"
        config_dir.mkdir()

        # Existing configs
        (config_dir / "local.yaml").write_text("name: Existing\n")
        (config_dir / "project.yaml").write_text("hostname: existing.com\n")

        # Legacy config with different values
        legacy_file = config_dir / "config.yaml"
        legacy_file.write_text("name: Legacy\nhostname: legacy.com\nemail: new@example.com\n")

        result = migrate_legacy_config(tmp_path)

        # Only new keys should be reported as migrated
        assert result["local"] == ["email"]
        assert result["project"] == []

        # Existing values should be preserved
        local = load_config(LOCAL, tmp_path)
        assert local["name"] == "Existing"  # Not overwritten
        assert local["email"] == "new@example.com"  # New value added

        project = load_config(PROJECT, tmp_path)
        assert project["hostname"] == "existing.com"  # Not overwritten


class TestConfigSingletonContains:
    """Tests for the 'in' operator on config singleton."""

    def test_contains_returns_true_for_existing_key(self, tmp_path):
        """Test 'key in config' returns True when key exists."""
        save_config(LOCAL, {"name": "John"}, tmp_path)
        config.reload(tmp_path)
        assert "name" in config

    def test_contains_returns_false_for_missing_key(self, tmp_path):
        """Test 'key in config' returns False when key doesn't exist."""
        config.reload(tmp_path)
        assert "name" not in config

    def test_contains_works_for_project_settings(self, tmp_path):
        """Test 'in' works for project config keys."""
        save_config(PROJECT, {"hostname": "example.com"}, tmp_path)
        config.reload(tmp_path)
        assert "hostname" in config
        assert "seed_command" not in config


class TestConfigSingletonDelattr:
    """Tests for deleting config values with 'del'."""

    def test_delete_local_config_key(self, tmp_path):
        """Test del config.name removes from local config."""
        save_config(LOCAL, {"name": "John", "email": "john@example.com"}, tmp_path)
        config.reload(tmp_path)

        del config.name

        assert "name" not in config
        assert config.name is None
        # Should be removed from file
        local = load_config(LOCAL, tmp_path)
        assert "name" not in local
        # Other keys should be preserved
        assert local["email"] == "john@example.com"

    def test_delete_project_config_key(self, tmp_path):
        """Test del config.hostname removes from project config."""
        save_config(PROJECT, {"hostname": "example.com", "project_name": "myproject"}, tmp_path)
        config.reload(tmp_path)

        del config.hostname

        assert "hostname" not in config
        assert config.hostname is None
        # Should be removed from file
        project = load_config(PROJECT, tmp_path)
        assert "hostname" not in project
        # Other keys should be preserved
        assert project["project_name"] == "myproject"

    def test_delete_missing_key_is_noop(self, tmp_path):
        """Test del config.missing_key doesn't raise."""
        config.reload(tmp_path)
        # Should not raise
        del config.seed_command
        assert "seed_command" not in config
