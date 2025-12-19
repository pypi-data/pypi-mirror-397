"""
Unit tests for ConfigManager class.

This module tests the ConfigManager which handles configuration precedence
(CLI → TOML → Default) and provides unified configuration access.
"""

import unittest

from unittest.mock import Mock, patch

from data_exchange_agent.config.manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test suite for ConfigManager class."""

    def test_initialization(self):
        """Test ConfigManager initialization."""
        manager = ConfigManager()

        self.assertIsNotNone(manager.cli_config)
        self.assertIsNotNone(manager.toml_config)
        self.assertIsNotNone(manager.default_config)

    def test_load_cli_config_with_namespace(self):
        """Test loading CLI config from argparse.Namespace."""
        manager = ConfigManager()

        # Create a mock argparse.Namespace
        args = Mock()
        args.__dict__ = {"workers": 8, "task_fetch_interval": 60, "debug_mode": True, "host": "127.0.0.1", "port": 8080}

        manager.load_cli_config(args)

        # Verify CLI config was loaded
        self.assertIsNotNone(manager.cli_config.application)
        self.assertEqual(manager.cli_config.application.workers, 8)

    def test_load_cli_config_with_dict(self):
        """Test loading CLI config from dictionary."""
        manager = ConfigManager()

        args_dict = {"workers": 10, "task_fetch_interval": 30, "debug_mode": False, "host": "localhost", "port": 9000}

        manager.load_cli_config(args_dict)

        # Verify CLI config was loaded
        self.assertIsNotNone(manager.cli_config.application)
        self.assertEqual(manager.cli_config.application.workers, 10)

    @patch("data_exchange_agent.config.manager.TomlConfig.load_config")
    def test_load_toml_config(self, mock_load):
        """Test loading TOML configuration."""
        manager = ConfigManager()
        test_path = "/path/to/config.toml"

        manager.load_toml_config(test_path)

        mock_load.assert_called_once_with(test_path)

    def test_get_with_existing_key(self):
        """Test get method with an existing key."""
        manager = ConfigManager()
        manager.default_config.application.workers = 4

        result = manager.get("application.workers", default=10)

        self.assertEqual(result, 4)

    def test_get_with_missing_key_returns_default(self):
        """Test get method with missing key returns default value."""
        manager = ConfigManager()

        result = manager.get("nonexistent.key", default="default_value")

        self.assertEqual(result, "default_value")

    def test_get_with_missing_key_returns_none(self):
        """Test get method with missing key and no default returns None."""
        manager = ConfigManager()

        result = manager.get("nonexistent.key")

        self.assertIsNone(result)

    def test_getitem_cli_precedence_over_toml(self):
        """Test that CLI config takes precedence over TOML config."""
        manager = ConfigManager()

        # Set both CLI and TOML configs
        manager.cli_config.application = Mock()
        manager.cli_config.application.workers = 8
        manager.toml_config.application = Mock()
        manager.toml_config.application.workers = 4

        result = manager["application.workers"]

        # CLI should take precedence
        self.assertEqual(result, 8)

    def test_getitem_toml_when_cli_none(self):
        """Test that TOML config is used when CLI is None."""
        manager = ConfigManager()

        # CLI returns None, TOML has value
        manager.cli_config.application = Mock()
        manager.cli_config.application.workers = None
        manager.toml_config.application = Mock()
        manager.toml_config.application.workers = 4

        result = manager["application.workers"]

        # TOML should be used
        self.assertEqual(result, 4)

    def test_getitem_default_when_cli_and_toml_none(self):
        """Test that default config is used when both CLI and TOML are None."""
        manager = ConfigManager()

        # Both CLI and TOML return None
        manager.cli_config.application = Mock()
        manager.cli_config.application.workers = None
        manager.toml_config.application = Mock()
        manager.toml_config.application.workers = None
        manager.default_config.application.workers = 4

        result = manager["application.workers"]

        # Default should be used
        self.assertEqual(result, 4)

    def test_getitem_raises_keyerror_when_not_found(self):
        """Test that __getitem__ raises KeyError when key not found anywhere."""
        manager = ConfigManager()

        with self.assertRaises(KeyError) as context:
            _ = manager["nonexistent.key"]

        self.assertIn("Configuration key 'nonexistent.key' not found", str(context.exception))

    def test_getitem_with_private_attribute_raises_error(self):
        """Test that accessing private attributes via __getitem__ raises KeyError."""
        manager = ConfigManager()

        with self.assertRaises(KeyError) as context:
            _ = manager["application._private"]

        self.assertIn("Private attributes cannot be accessed via indexing", str(context.exception))

    def test_getitem_with_nested_private_attribute_raises_error(self):
        """Test that nested private attributes raise KeyError."""
        manager = ConfigManager()

        with self.assertRaises(KeyError) as context:
            _ = manager["_private.key"]

        self.assertIn("Private attributes cannot be accessed via indexing", str(context.exception))

    def test_get_value_with_dict(self):
        """Test _get_value method with dictionary access."""
        manager = ConfigManager()

        test_dict = {"level1": {"level2": {"level3": "value"}}}
        result = manager._get_value(["level1", "level2", "level3"], test_dict)

        self.assertEqual(result, "value")

    def test_get_value_with_object(self):
        """Test _get_value method with object attribute access."""
        manager = ConfigManager()

        test_obj = Mock()
        test_obj.attr1 = Mock()
        test_obj.attr1.attr2 = "value"

        result = manager._get_value(["attr1", "attr2"], test_obj)

        self.assertEqual(result, "value")

    def test_get_value_returns_none_on_missing_key(self):
        """Test _get_value returns None when key doesn't exist."""
        manager = ConfigManager()

        test_dict = {"level1": {"level2": "value"}}
        result = manager._get_value(["level1", "nonexistent"], test_dict)

        self.assertIsNone(result)

    def test_get_value_returns_none_on_attribute_error(self):
        """Test _get_value returns None on AttributeError."""
        manager = ConfigManager()

        test_obj = Mock()
        test_obj.attr1 = "not_an_object"

        result = manager._get_value(["attr1", "attr2"], test_obj)

        self.assertIsNone(result)

    def test_repr(self):
        """Test string representation of ConfigManager."""
        manager = ConfigManager()

        repr_str = repr(manager)

        self.assertIn("ConfigManager", repr_str)
        self.assertIn("cli_config", repr_str)
        self.assertIn("toml_config", repr_str)


class TestConfigManagerEdgeCases(unittest.TestCase):
    """Test edge cases and error handling in ConfigManager."""

    def test_getitem_with_empty_string(self):
        """Test __getitem__ with empty string key."""
        manager = ConfigManager()

        with self.assertRaises(KeyError):
            _ = manager[""]

    def test_getitem_with_single_part(self):
        """Test __getitem__ with single part key (no dots)."""
        manager = ConfigManager()
        manager.default_config.simple = "value"

        result = manager["simple"]

        self.assertEqual(result, "value")

    def test_getitem_with_many_parts(self):
        """Test __getitem__ with deeply nested key."""
        manager = ConfigManager()

        # Create deeply nested structure
        manager.default_config.a = Mock()
        manager.default_config.a.b = Mock()
        manager.default_config.a.b.c = Mock()
        manager.default_config.a.b.c.d = "deep_value"

        result = manager["a.b.c.d"]

        self.assertEqual(result, "deep_value")

    def test_get_value_with_empty_parts(self):
        """Test _get_value with empty parts list."""
        manager = ConfigManager()
        test_obj = Mock()

        result = manager._get_value([], test_obj)

        # Should return the root object
        self.assertIs(result, test_obj)

    def test_mixed_dict_and_object_access(self):
        """Test _get_value with mixed dictionary and object access."""
        manager = ConfigManager()

        # Create mixed structure
        test_dict = {"dict_level": Mock()}
        test_dict["dict_level"].obj_level = "value"

        result = manager._get_value(["dict_level", "obj_level"], test_dict)

        self.assertEqual(result, "value")


if __name__ == "__main__":
    unittest.main()
