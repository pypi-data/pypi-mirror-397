"""
Unit tests for CLIConfig class.

This module tests the CLIConfig which manages command-line
interface configuration parameters.
"""

import unittest

from argparse import Namespace
from unittest.mock import Mock

from data_exchange_agent.config.cli import CLIConfig


class TestCLIConfig(unittest.TestCase):
    """Test suite for CLIConfig class."""

    def test_initialization(self):
        """Test CLIConfig initialization."""
        config = CLIConfig()

        self.assertIsNone(config.application)
        self.assertIsNone(config.server)

    def test_repr(self):
        """Test string representation of CLIConfig."""
        config = CLIConfig()

        repr_str = repr(config)

        self.assertIn("CLIConfig", repr_str)
        self.assertIn("application", repr_str)
        self.assertIn("server", repr_str)

    def test_load_config_from_args_with_namespace(self):
        """Test loading config from argparse.Namespace."""
        config = CLIConfig()

        args = Namespace(workers=8, task_fetch_interval=60, debug_mode=True, host="127.0.0.1", port=8080)

        config.load_config(args)

        self.assertIsNotNone(config.application)
        self.assertIsNotNone(config.server)
        self.assertEqual(config.application.workers, 8)
        self.assertEqual(config.application.task_fetch_interval, 60)
        self.assertTrue(config.application.debug_mode)
        self.assertEqual(config.server.host, "127.0.0.1")
        self.assertEqual(config.server.port, 8080)

    def test_load_config_from_dict(self):
        """Test loading config from dictionary."""
        config = CLIConfig()

        config_dict = {"workers": 10, "task_fetch_interval": 30, "debug_mode": False, "host": "localhost", "port": 9000}

        config.load_config(config_dict)

        self.assertIsNotNone(config.application)
        self.assertIsNotNone(config.server)
        self.assertEqual(config.application.workers, 10)
        self.assertEqual(config.application.task_fetch_interval, 30)
        self.assertFalse(config.application.debug_mode)
        self.assertEqual(config.server.host, "localhost")
        self.assertEqual(config.server.port, 9000)

    def test_load_config_from_args_delegates_to_dict(self):
        """Test that load_config_from_args delegates to load_config_from_dict."""
        config = CLIConfig()

        args = Mock()
        args.__dict__ = {"workers": 5, "task_fetch_interval": 120, "debug_mode": True, "host": "0.0.0.0", "port": 5000}

        config.load_config(args)

        self.assertEqual(config.application.workers, 5)
        self.assertEqual(config.server.port, 5000)

    def test_load_config_with_partial_values(self):
        """Test loading config with some None values."""
        config = CLIConfig()

        config_dict = {"workers": 4, "task_fetch_interval": None, "debug_mode": None, "host": "localhost", "port": None}

        config.load_config(config_dict)

        self.assertEqual(config.application.workers, 4)
        self.assertIsNone(config.application.task_fetch_interval)
        self.assertIsNone(config.application.debug_mode)
        self.assertEqual(config.server.host, "localhost")
        self.assertIsNone(config.server.port)

    def test_load_config_with_all_none(self):
        """Test loading config with all None values."""
        config = CLIConfig()

        config_dict = {"workers": None, "task_fetch_interval": None, "debug_mode": None, "host": None, "port": None}

        config.load_config(config_dict)

        self.assertIsNone(config.application.workers)
        self.assertIsNone(config.application.task_fetch_interval)
        self.assertIsNone(config.application.debug_mode)
        self.assertIsNone(config.server.host)
        self.assertIsNone(config.server.port)

    def test_load_config_with_missing_keys(self):
        """Test loading config with missing keys uses get default None."""
        config = CLIConfig()

        config_dict = {
            # Only provide workers, omit others
            "workers": 6
        }

        config.load_config(config_dict)

        self.assertEqual(config.application.workers, 6)
        self.assertIsNone(config.application.task_fetch_interval)
        self.assertIsNone(config.application.debug_mode)
        self.assertIsNone(config.server.host)
        self.assertIsNone(config.server.port)

    def test_load_config_with_empty_dict(self):
        """Test loading config with empty dictionary."""
        config = CLIConfig()

        config_dict = {}

        config.load_config(config_dict)

        self.assertIsNotNone(config.application)
        self.assertIsNotNone(config.server)
        self.assertIsNone(config.application.workers)
        self.assertIsNone(config.server.port)


class TestCLIConfigIntegration(unittest.TestCase):
    """Test CLIConfig integration with ApplicationConfig and ServerConfig."""

    def test_application_config_created_correctly(self):
        """Test that ApplicationConfig is created correctly."""
        from data_exchange_agent.config.sections.application import ApplicationConfig

        config = CLIConfig()
        config_dict = {"workers": 8, "task_fetch_interval": 60, "debug_mode": True, "host": "localhost", "port": 5000}

        config.load_config(config_dict)

        self.assertIsInstance(config.application, ApplicationConfig)

    def test_server_config_created_correctly(self):
        """Test that ServerConfig is created correctly."""
        from data_exchange_agent.config.sections.server import ServerConfig

        config = CLIConfig()
        config_dict = {"workers": 8, "task_fetch_interval": 60, "debug_mode": True, "host": "localhost", "port": 5000}

        config.load_config(config_dict)

        self.assertIsInstance(config.server, ServerConfig)

    def test_invalid_application_values_raise_error(self):
        """Test that invalid application values raise ValueError."""
        config = CLIConfig()

        config_dict = {
            "workers": -1,  # Invalid
            "task_fetch_interval": 60,
            "debug_mode": True,
            "host": "localhost",
            "port": 5000,
        }

        with self.assertRaises(ValueError):
            config.load_config(config_dict)

    def test_invalid_server_values_raise_error(self):
        """Test that invalid server values raise ValueError."""
        config = CLIConfig()

        config_dict = {
            "workers": 4,
            "task_fetch_interval": 60,
            "debug_mode": True,
            "host": "localhost",
            "port": 70000,  # Invalid
        }

        with self.assertRaises(ValueError):
            config.load_config(config_dict)

    def test_reload_config_overwrites_previous(self):
        """Test that reloading config overwrites previous values."""
        config = CLIConfig()

        # First load
        config_dict1 = {"workers": 4, "task_fetch_interval": 60, "debug_mode": True, "host": "localhost", "port": 5000}
        config.load_config(config_dict1)

        self.assertEqual(config.application.workers, 4)

        # Second load
        config_dict2 = {"workers": 8, "task_fetch_interval": 30, "debug_mode": False, "host": "0.0.0.0", "port": 8080}
        config.load_config(config_dict2)

        self.assertEqual(config.application.workers, 8)
        self.assertEqual(config.application.task_fetch_interval, 30)
        self.assertFalse(config.application.debug_mode)


class TestCLIConfigEdgeCases(unittest.TestCase):
    """Test edge cases for CLIConfig."""

    def test_load_with_extra_keys(self):
        """Test loading config with extra keys that are ignored."""
        config = CLIConfig()

        config_dict = {
            "workers": 4,
            "task_fetch_interval": 60,
            "debug_mode": True,
            "host": "localhost",
            "port": 5000,
            "extra_key": "extra_value",  # Should be ignored
            "another_key": 123,  # Should be ignored
        }

        # Should not raise error
        config.load_config(config_dict)

        self.assertEqual(config.application.workers, 4)
        self.assertEqual(config.server.port, 5000)

    def test_namespace_without_all_keys(self):
        """Test Namespace without all expected keys."""
        config = CLIConfig()

        # Namespace with only some keys
        args = Mock()
        args.__dict__ = {
            "workers": 8
            # Missing other keys
        }

        config.load_config(args)

        self.assertEqual(config.application.workers, 8)
        self.assertIsNone(config.application.task_fetch_interval)

    def test_access_config_before_loading(self):
        """Test accessing config properties before loading."""
        config = CLIConfig()

        # Should be None before loading
        self.assertIsNone(config.application)
        self.assertIsNone(config.server)


if __name__ == "__main__":
    unittest.main()
