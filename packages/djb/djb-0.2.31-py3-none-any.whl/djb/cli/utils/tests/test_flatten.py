"""Tests for djb.cli.utils.flatten module."""

from __future__ import annotations

from djb.cli.utils.flatten import flatten_dict


class TestFlattenDict:
    """Tests for flatten_dict function."""

    def test_empty_dict(self):
        """Test flattening empty dict."""
        result = flatten_dict({})
        assert result == {}

    def test_flat_dict(self):
        """Test flattening already flat dict."""
        result = flatten_dict({"key": "value", "other": "data"})
        assert result == {"KEY": "value", "OTHER": "data"}

    def test_nested_dict(self):
        """Test flattening nested dict."""
        result = flatten_dict({"db": {"host": "localhost", "port": 5432}})
        assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}

    def test_deeply_nested_dict(self):
        """Test flattening deeply nested dict."""
        result = flatten_dict({"a": {"b": {"c": "value"}}})
        assert result == {"A_B_C": "value"}

    def test_mixed_nesting(self):
        """Test flattening dict with mixed nesting levels."""
        result = flatten_dict(
            {
                "simple": "value",
                "nested": {"key": "data"},
                "deep": {"level1": {"level2": "deep_value"}},
            }
        )
        assert result == {
            "SIMPLE": "value",
            "NESTED_KEY": "data",
            "DEEP_LEVEL1_LEVEL2": "deep_value",
        }

    def test_converts_non_string_values(self):
        """Test converts non-string values to strings."""
        result = flatten_dict({"count": 42, "enabled": True, "ratio": 3.14})
        assert result == {"COUNT": "42", "ENABLED": "True", "RATIO": "3.14"}

    def test_uppercase_keys(self):
        """Test all keys are uppercased."""
        result = flatten_dict({"mixedCase": "value", "UPPER": "data", "lower": "test"})
        assert result == {"MIXEDCASE": "value", "UPPER": "data", "LOWER": "test"}
