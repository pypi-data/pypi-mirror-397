"""Tests for djb.secrets.paths module."""

from __future__ import annotations

from unittest.mock import patch

from djb.secrets.paths import (
    get_default_key_path,
    get_default_secrets_dir,
    get_encrypted_key_path,
)


class TestGetDefaultKeyPath:
    """Tests for get_default_key_path."""

    def test_returns_age_keys_path(self, tmp_path):
        """Test default key path is .age/keys.txt in project root."""
        with patch("djb.secrets.paths.find_project_root", return_value=tmp_path):
            result = get_default_key_path()
            assert result == tmp_path / ".age" / "keys.txt"

    def test_uses_provided_project_root(self, tmp_path):
        """Test using explicit project root."""
        result = get_default_key_path(tmp_path)
        assert result == tmp_path / ".age" / "keys.txt"


class TestGetDefaultSecretsDir:
    """Tests for get_default_secrets_dir."""

    def test_returns_secrets_in_cwd(self, tmp_path, monkeypatch):
        """Test default secrets dir is secrets/ in cwd."""
        monkeypatch.chdir(tmp_path)
        result = get_default_secrets_dir()
        assert result == tmp_path / "secrets"

    def test_uses_provided_project_root(self, tmp_path):
        """Test using explicit project root."""
        result = get_default_secrets_dir(tmp_path)
        assert result == tmp_path / "secrets"


class TestGetEncryptedKeyPath:
    """Tests for get_encrypted_key_path."""

    def test_appends_gpg_suffix(self, tmp_path):
        """Test appends .gpg suffix to key path."""
        key_path = tmp_path / ".age" / "keys.txt"
        result = get_encrypted_key_path(key_path)
        assert result == tmp_path / ".age" / "keys.txt.gpg"

    def test_preserves_parent_directory(self, tmp_path):
        """Test preserves the parent directory."""
        key_path = tmp_path / "custom" / "dir" / "mykey.txt"
        result = get_encrypted_key_path(key_path)
        assert result.parent == key_path.parent
