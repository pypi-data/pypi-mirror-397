"""
Unit tests for TomlConfig class.

This module tests the TomlConfig which loads configuration from TOML files
and manages task sources and connection configurations.
"""

import unittest

from unittest.mock import Mock, mock_open, patch

from data_exchange_agent import custom_exceptions
from data_exchange_agent.config.toml import TomlConfig


class TestTomlConfig(unittest.TestCase):
    """Test suite for TomlConfig class."""

    def test_initialization(self):
        """Test TomlConfig initialization."""
        config = TomlConfig()

        self.assertIsNone(config.selected_task_source)
        self.assertIsNone(config.application)
        self.assertIsNone(config.task_source)
        self.assertIsInstance(config.connections, dict)
        self.assertIn("source", config.connections)
        self.assertIn("target", config.connections)

    def test_connections_initialized_with_empty_dicts(self):
        """Test that connections dict is initialized with empty source/target dicts."""
        config = TomlConfig()

        self.assertIsInstance(config.connections["source"], dict)
        self.assertIsInstance(config.connections["target"], dict)
        self.assertEqual(len(config.connections["source"]), 0)
        self.assertEqual(len(config.connections["target"]), 0)

    def test_repr(self):
        """Test string representation of TomlConfig."""
        config = TomlConfig()

        repr_str = repr(config)

        self.assertIn("TomlConfig", repr_str)
        self.assertIn("selected_task_source", repr_str)
        self.assertIn("application", repr_str)
        self.assertIn("task_source", repr_str)
        self.assertIn("connections", repr_str)


class TestTomlConfigLoadFromDict(unittest.TestCase):
    """Test loading configuration from dictionary."""

    def test_load_selected_task_source(self):
        """Test loading selected_task_source from dict."""
        config = TomlConfig()

        config_dict = {"selected_task_source": "api"}

        config.load_config(config_dict)

        self.assertEqual(config.selected_task_source, "api")

    def test_load_application_config(self):
        """Test loading application config from dict."""
        config = TomlConfig()

        config_dict = {"application": {"workers": 8, "task_fetch_interval": 60, "debug_mode": True}}

        config.load_config(config_dict)

        self.assertIsNotNone(config.application)
        self.assertEqual(config.application.workers, 8)
        self.assertEqual(config.application.task_fetch_interval, 60)
        self.assertTrue(config.application.debug_mode)

    @patch("data_exchange_agent.config.toml.TaskSourceRegistry.create")
    def test_load_task_source_config(self, mock_create):
        """Test loading task source config from dict."""
        config = TomlConfig()
        mock_task_source = Mock()
        mock_create.return_value = mock_task_source

        config_dict = {"selected_task_source": "api", "task_source": {"api": {"key": "test_key"}}}

        config.load_config(config_dict)

        self.assertEqual(config.task_source, mock_task_source)
        mock_create.assert_called_once_with("api", key="test_key")

    @patch("data_exchange_agent.config.toml.ConnectionRegistry.create")
    def test_load_source_connections(self, mock_create):
        """Test loading source connections from dict."""
        config = TomlConfig()
        mock_connection = Mock()
        mock_create.return_value = mock_connection

        config_dict = {"connections": {"source": {"postgresql": {"host": "localhost", "port": 5432}}}}

        config.load_config(config_dict)

        self.assertIn("postgresql", config.connections["source"])
        mock_create.assert_called_once()

    @patch("data_exchange_agent.config.toml.ConnectionRegistry.create")
    def test_load_target_connections(self, mock_create):
        """Test loading target connections from dict."""
        config = TomlConfig()
        mock_connection = Mock()
        mock_create.return_value = mock_connection

        config_dict = {"connections": {"target": {"s3": {"bucket_name": "test-bucket", "profile_name": "default"}}}}

        config.load_config(config_dict)

        self.assertIn("s3", config.connections["target"])
        mock_create.assert_called_once()

    @patch("data_exchange_agent.config.toml.ConnectionRegistry.create")
    def test_load_multiple_connections(self, mock_create):
        """Test loading multiple connections from dict."""
        config = TomlConfig()
        mock_connection = Mock()
        mock_create.return_value = mock_connection

        config_dict = {
            "connections": {
                "source": {"postgresql": {"host": "localhost"}, "sqlserver": {"host": "server"}},
                "target": {"s3": {"bucket_name": "bucket"}, "snowflake_password": {"account": "account"}},
            }
        }

        config.load_config(config_dict)

        self.assertEqual(len(config.connections["source"]), 2)
        self.assertEqual(len(config.connections["target"]), 2)

    def test_load_with_empty_dict(self):
        """Test loading from empty dictionary."""
        config = TomlConfig()

        config.load_config({})

        self.assertIsNone(config.selected_task_source)
        self.assertIsNone(config.application)
        self.assertIsNone(config.task_source)

    def test_load_task_source_without_selected_task_source(self):
        """Test that task_source is not loaded if selected_task_source is not set."""
        config = TomlConfig()

        config_dict = {"task_source": {"api": {"key": "test_key"}}}

        with self.assertRaises(custom_exceptions.ConfigurationError) as context:
            config.load_config(config_dict)

        self.assertIn("must be set to use 'task_source' configuration", str(context.exception))


class TestTomlConfigLoadFromFile(unittest.TestCase):
    """Test loading configuration from TOML file."""

    @patch("data_exchange_agent.config.toml.toml.load")
    def test_load_from_toml_file(self, mock_toml_load):
        """Test loading config from TOML file."""
        config = TomlConfig()

        mock_toml_load.return_value = {"selected_task_source": "api", "application": {"workers": 4}}

        config.load_config("/path/to/config.toml")

        mock_toml_load.assert_called_once_with("/path/to/config.toml")
        self.assertEqual(config.selected_task_source, "api")

    @patch("data_exchange_agent.config.toml.toml.load")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_from_toml_file_toml_decode_error(self, mock_file, mock_toml_load):
        """Test that TomlDecodeError is caught and wrapped."""
        import toml

        config = TomlConfig()

        mock_toml_load.side_effect = toml.TomlDecodeError("Invalid TOML", "doc", 1)

        with self.assertRaises(custom_exceptions.ConfigurationError) as context:
            config.load_config("/path/to/config.toml")

        self.assertIn("valid TOML file", str(context.exception))

    @patch("data_exchange_agent.config.toml.toml.load")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_from_toml_file_os_error(self, mock_file, mock_toml_load):
        """Test that OSError is caught and wrapped."""
        config = TomlConfig()

        mock_toml_load.side_effect = OSError("File not found")

        with self.assertRaises(custom_exceptions.ConfigurationError) as context:
            config.load_config("/path/to/config.toml")

        self.assertIn("exists and is readable", str(context.exception))

    @patch("data_exchange_agent.config.toml.toml.load")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_from_toml_file_type_error(self, mock_file, mock_toml_load):
        """Test that TypeError is caught and wrapped."""
        config = TomlConfig()

        mock_toml_load.side_effect = TypeError("Invalid type")

        with self.assertRaises(custom_exceptions.ConfigurationError) as context:
            config.load_config("/path/to/config.toml")

        self.assertIn("Invalid configuration data", str(context.exception))

    @patch("data_exchange_agent.config.toml.toml.load")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_from_toml_file_value_error(self, mock_file, mock_toml_load):
        """Test that ValueError is caught and wrapped."""
        config = TomlConfig()

        mock_toml_load.side_effect = ValueError("Invalid value")

        with self.assertRaises(custom_exceptions.ConfigurationError) as context:
            config.load_config("/path/to/config.toml")

        self.assertIn("Invalid configuration data", str(context.exception))

    @patch("data_exchange_agent.config.toml.toml.load")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_from_toml_file_unexpected_exception(self, mock_file, mock_toml_load):
        """Test that unexpected exceptions are caught and wrapped."""
        config = TomlConfig()

        mock_toml_load.side_effect = RuntimeError("Unexpected error")

        with self.assertRaises(custom_exceptions.ConfigurationError) as context:
            config.load_config("/path/to/config.toml")

        self.assertIn("Unexpected error", str(context.exception))


class TestTomlConfigIntegration(unittest.TestCase):
    """Test TomlConfig integration with other components."""

    def test_application_config_type(self):
        """Test that loaded application config is ApplicationConfig instance."""
        from data_exchange_agent.config.sections.application import ApplicationConfig

        config = TomlConfig()
        config_dict = {"application": {"workers": 4, "task_fetch_interval": 120, "debug_mode": False}}

        config.load_config(config_dict)

        self.assertIsInstance(config.application, ApplicationConfig)

    @patch("data_exchange_agent.config.toml.TaskSourceRegistry.create")
    def test_task_source_registry_integration(self, mock_create):
        """Test integration with TaskSourceRegistry."""
        config = TomlConfig()
        mock_task_source = Mock()
        mock_create.return_value = mock_task_source

        config_dict = {"selected_task_source": "api", "task_source": {"api": {"key": "test_key"}}}

        config.load_config(config_dict)

        # Should call registry.create with correct parameters
        mock_create.assert_called_once_with("api", key="test_key")

    @patch("data_exchange_agent.config.toml.ConnectionRegistry.create")
    def test_connection_registry_integration(self, mock_create):
        """Test integration with ConnectionRegistry."""
        config = TomlConfig()
        mock_connection = Mock()
        mock_create.return_value = mock_connection

        config_dict = {
            "connections": {
                "source": {
                    "postgresql": {
                        "username": "user",
                        "password": "pass",
                        "database": "db",
                        "host": "localhost",
                        "port": 5432,
                    }
                }
            }
        }

        config.load_config(config_dict)

        # Should call registry.create
        mock_create.assert_called_once()


class TestTomlConfigEdgeCases(unittest.TestCase):
    """Test edge cases for TomlConfig."""

    def test_task_source_missing_selected_source(self):
        """Test task_source config when selected_task_source doesn't match."""
        config = TomlConfig()

        config_dict = {
            "selected_task_source": "api",
            "task_source": {"database": {"connection": "test"}},  # Different from selected_task_source
        }

        config.load_config(config_dict)

        # task_source should not be loaded
        self.assertIsNone(config.task_source)

    def test_connections_with_only_source(self):
        """Test loading connections with only source section."""
        config = TomlConfig()

        config_dict = {
            "connections": {
                "source": {
                    "postgresql": {
                        "username": "user",
                        "password": "pass",
                        "database": "db",
                        "host": "localhost",
                        "port": 5432,
                    }
                }
            }
        }

        config.load_config(config_dict)

        # Target should still be empty
        self.assertEqual(len(config.connections["target"]), 0)

    def test_connections_with_only_target(self):
        """Test loading connections with only target section."""
        config = TomlConfig()

        config_dict = {"connections": {"target": {"snowflake_connection_name": {"connection_name": "test-connection"}}}}

        config.load_config(config_dict)

        # Source should still be empty
        self.assertEqual(len(config.connections["source"]), 0)

    def test_reload_config_overwrites_previous(self):
        """Test that reloading config overwrites previous values."""
        config = TomlConfig()

        # First load
        config_dict1 = {"selected_task_source": "api", "application": {"workers": 4}}
        config.load_config(config_dict1)

        self.assertEqual(config.selected_task_source, "api")

        # Second load
        config_dict2 = {"selected_task_source": "database", "application": {"workers": 8}}
        config.load_config(config_dict2)

        self.assertEqual(config.selected_task_source, "database")
        self.assertEqual(config.application.workers, 8)


if __name__ == "__main__":
    unittest.main()
