"""
Unit tests for DefaultConfig class.

This module tests the DefaultConfig which provides default values
for application and server configuration when not specified elsewhere.
"""

import unittest

from data_exchange_agent.config.default import DefaultConfig
from data_exchange_agent.constants.config_defaults import (
    DEFAULT__APPLICATION__DEBUG_MODE,
    DEFAULT__APPLICATION__TASK_FETCH_INTERVAL,
    DEFAULT__APPLICATION__WORKERS,
    DEFAULT__SERVER__HOST,
    DEFAULT__SERVER__PORT,
)


class TestDefaultConfig(unittest.TestCase):
    """Test suite for DefaultConfig class."""

    def test_initialization(self):
        """Test DefaultConfig initialization."""
        config = DefaultConfig()

        self.assertIsNotNone(config.application)
        self.assertIsNotNone(config.server)

    def test_application_config_initialized(self):
        """Test that application config is initialized with defaults."""
        config = DefaultConfig()

        self.assertEqual(config.application.workers, DEFAULT__APPLICATION__WORKERS)
        self.assertEqual(config.application.task_fetch_interval, DEFAULT__APPLICATION__TASK_FETCH_INTERVAL)
        self.assertEqual(config.application.debug_mode, DEFAULT__APPLICATION__DEBUG_MODE)

    def test_server_config_initialized(self):
        """Test that server config is initialized with defaults."""
        config = DefaultConfig()

        self.assertEqual(config.server.host, DEFAULT__SERVER__HOST)
        self.assertEqual(config.server.port, DEFAULT__SERVER__PORT)

    def test_application_workers_default(self):
        """Test default workers value."""
        config = DefaultConfig()

        self.assertEqual(config.application.workers, 4)
        self.assertIsInstance(config.application.workers, int)

    def test_application_task_fetch_interval_default(self):
        """Test default task_fetch_interval value."""
        config = DefaultConfig()

        self.assertEqual(config.application.task_fetch_interval, 120)
        self.assertIsInstance(config.application.task_fetch_interval, int)

    def test_application_debug_mode_default(self):
        """Test default debug_mode value."""
        config = DefaultConfig()

        self.assertFalse(config.application.debug_mode)
        self.assertIsInstance(config.application.debug_mode, bool)

    def test_server_host_default(self):
        """Test default host value."""
        config = DefaultConfig()

        self.assertEqual(config.server.host, "0.0.0.0")
        self.assertIsInstance(config.server.host, str)

    def test_server_port_default(self):
        """Test default port value."""
        config = DefaultConfig()

        self.assertEqual(config.server.port, 5001)
        self.assertIsInstance(config.server.port, int)

    def test_repr(self):
        """Test string representation of DefaultConfig."""
        config = DefaultConfig()

        repr_str = repr(config)

        self.assertIn("DefaultConfig", repr_str)
        self.assertIn("application", repr_str)
        self.assertIn("server", repr_str)

    def test_application_is_application_config(self):
        """Test that application is an instance of ApplicationConfig."""
        from data_exchange_agent.config.sections.application import ApplicationConfig

        config = DefaultConfig()

        self.assertIsInstance(config.application, ApplicationConfig)

    def test_server_is_server_config(self):
        """Test that server is an instance of ServerConfig."""
        from data_exchange_agent.config.sections.server import ServerConfig

        config = DefaultConfig()

        self.assertIsInstance(config.server, ServerConfig)

    def test_multiple_instances_have_same_defaults(self):
        """Test that multiple instances have the same default values."""
        config1 = DefaultConfig()
        config2 = DefaultConfig()

        self.assertEqual(config1.application.workers, config2.application.workers)
        self.assertEqual(config1.application.task_fetch_interval, config2.application.task_fetch_interval)
        self.assertEqual(config1.application.debug_mode, config2.application.debug_mode)
        self.assertEqual(config1.server.host, config2.server.host)
        self.assertEqual(config1.server.port, config2.server.port)

    def test_multiple_instances_are_independent(self):
        """Test that multiple instances are independent objects."""
        config1 = DefaultConfig()
        config2 = DefaultConfig()

        # Should be different instances
        self.assertIsNot(config1, config2)
        self.assertIsNot(config1.application, config2.application)
        self.assertIsNot(config1.server, config2.server)


class TestDefaultConfigValues(unittest.TestCase):
    """Test that default values are sensible and valid."""

    def test_workers_is_positive(self):
        """Test that default workers is positive."""
        config = DefaultConfig()

        self.assertGreater(config.application.workers, 0)

    def test_workers_is_reasonable(self):
        """Test that default workers is within reasonable bounds."""
        config = DefaultConfig()

        self.assertGreaterEqual(config.application.workers, 1)
        self.assertLessEqual(config.application.workers, 100)

    def test_task_fetch_interval_is_positive(self):
        """Test that default task_fetch_interval is positive."""
        config = DefaultConfig()

        self.assertGreater(config.application.task_fetch_interval, 0)

    def test_task_fetch_interval_is_reasonable(self):
        """Test that default task_fetch_interval is reasonable (not too short)."""
        config = DefaultConfig()

        # Should be at least 1 second
        self.assertGreaterEqual(config.application.task_fetch_interval, 1)

    def test_port_is_valid(self):
        """Test that default port is within valid range."""
        config = DefaultConfig()

        self.assertGreaterEqual(config.server.port, 1)
        self.assertLessEqual(config.server.port, 65535)

    def test_host_is_valid_format(self):
        """Test that default host is a valid format."""
        config = DefaultConfig()

        # Should be a string
        self.assertIsInstance(config.server.host, str)
        # Should not be empty
        self.assertTrue(config.server.host)

    def test_debug_mode_is_false_by_default(self):
        """Test that debug mode is False by default (production-safe)."""
        config = DefaultConfig()

        # Default should be False for production safety
        self.assertFalse(config.application.debug_mode)


class TestDefaultConfigIntegration(unittest.TestCase):
    """Test DefaultConfig integration with constant definitions."""

    def test_uses_defined_constants(self):
        """Test that DefaultConfig uses the defined constants."""
        config = DefaultConfig()

        # Should match the constants exactly
        self.assertEqual(config.application.workers, DEFAULT__APPLICATION__WORKERS)
        self.assertEqual(config.application.task_fetch_interval, DEFAULT__APPLICATION__TASK_FETCH_INTERVAL)
        self.assertEqual(config.application.debug_mode, DEFAULT__APPLICATION__DEBUG_MODE)
        self.assertEqual(config.server.host, DEFAULT__SERVER__HOST)
        self.assertEqual(config.server.port, DEFAULT__SERVER__PORT)

    def test_constants_are_valid_for_configs(self):
        """Test that constant values pass config validation."""
        # Creating DefaultConfig should not raise any validation errors
        config = DefaultConfig()

        # If we got here, the constants passed validation
        self.assertIsNotNone(config)

    def test_can_access_via_attribute(self):
        """Test that default config values are accessible via attributes."""
        config = DefaultConfig()

        # Direct attribute access
        self.assertEqual(config.application.workers, DEFAULT__APPLICATION__WORKERS)
        self.assertEqual(config.server.port, DEFAULT__SERVER__PORT)

    def test_config_objects_have_getitem(self):
        """Test that config objects support dictionary-style access."""
        config = DefaultConfig()

        # Should support __getitem__ from BaseConfig
        self.assertEqual(config.application["workers"], DEFAULT__APPLICATION__WORKERS)
        self.assertEqual(config.server["port"], DEFAULT__SERVER__PORT)


class TestDefaultConfigEdgeCases(unittest.TestCase):
    """Test edge cases for DefaultConfig."""

    def test_modifying_instance_doesnt_affect_others(self):
        """Test that modifying one instance doesn't affect others."""
        config1 = DefaultConfig()
        config2 = DefaultConfig()

        # Modify config1
        config1.application.workers = 99

        # config2 should still have default value
        self.assertEqual(config2.application.workers, DEFAULT__APPLICATION__WORKERS)

    def test_modifying_instance_doesnt_affect_constants(self):
        """Test that modifying instance doesn't affect the constants."""
        config = DefaultConfig()
        original_default = DEFAULT__APPLICATION__WORKERS

        # Modify config
        config.application.workers = 99

        # Constant should be unchanged
        self.assertEqual(DEFAULT__APPLICATION__WORKERS, original_default)

    def test_repr_is_informative(self):
        """Test that repr provides useful information."""
        config = DefaultConfig()

        repr_str = repr(config)

        # Should contain class name and config info
        self.assertIn("DefaultConfig", repr_str)
        # Should show the config objects
        self.assertTrue("application" in repr_str or "server" in repr_str)


if __name__ == "__main__":
    unittest.main()
