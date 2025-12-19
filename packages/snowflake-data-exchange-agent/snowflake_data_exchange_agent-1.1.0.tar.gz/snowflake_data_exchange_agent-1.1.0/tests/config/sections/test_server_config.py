"""
Unit tests for ServerConfig class.

This module tests the ServerConfig which manages server settings
like host address and port number.
"""

import unittest

from data_exchange_agent.config.sections.server import ServerConfig


class TestServerConfig(unittest.TestCase):
    """Test suite for ServerConfig class."""

    def test_initialization_with_all_none(self):
        """Test ServerConfig initialization with all None values."""
        config = ServerConfig()

        self.assertIsNone(config.host)
        self.assertIsNone(config.port)

    def test_initialization_with_values(self):
        """Test ServerConfig initialization with actual values."""
        config = ServerConfig(host="0.0.0.0", port=5000)

        self.assertEqual(config.host, "0.0.0.0")
        self.assertEqual(config.port, 5000)

    def test_initialization_with_partial_values(self):
        """Test ServerConfig initialization with some None values."""
        config = ServerConfig(host="localhost", port=None)

        self.assertEqual(config.host, "localhost")
        self.assertIsNone(config.port)

    def test_valid_host_localhost(self):
        """Test ServerConfig with valid host 'localhost'."""
        config = ServerConfig(host="localhost")

        self.assertEqual(config.host, "localhost")

    def test_valid_host_ip_address(self):
        """Test ServerConfig with valid IP address."""
        config = ServerConfig(host="192.168.1.1")

        self.assertEqual(config.host, "192.168.1.1")

    def test_valid_host_domain_name(self):
        """Test ServerConfig with valid domain name."""
        config = ServerConfig(host="example.com")

        self.assertEqual(config.host, "example.com")

    def test_valid_host_all_interfaces(self):
        """Test ServerConfig with 0.0.0.0 (all interfaces)."""
        config = ServerConfig(host="0.0.0.0")

        self.assertEqual(config.host, "0.0.0.0")

    def test_host_invalid_type_raises_error(self):
        """Test that non-string host raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ServerConfig(host=12345)

        self.assertIn("Host must be a string", str(context.exception))

    def test_host_list_raises_error(self):
        """Test that list host raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ServerConfig(host=["localhost"])

        self.assertIn("Host must be a string", str(context.exception))

    def test_valid_port_1(self):
        """Test ServerConfig with minimum valid port (1)."""
        config = ServerConfig(port=1)

        self.assertEqual(config.port, 1)

    def test_valid_port_65535(self):
        """Test ServerConfig with maximum valid port (65535)."""
        config = ServerConfig(port=65535)

        self.assertEqual(config.port, 65535)

    def test_valid_port_common_http(self):
        """Test ServerConfig with common HTTP port (80)."""
        config = ServerConfig(port=80)

        self.assertEqual(config.port, 80)

    def test_valid_port_common_https(self):
        """Test ServerConfig with common HTTPS port (443)."""
        config = ServerConfig(port=443)

        self.assertEqual(config.port, 443)

    def test_valid_port_5000(self):
        """Test ServerConfig with port 5000."""
        config = ServerConfig(port=5000)

        self.assertEqual(config.port, 5000)

    def test_port_zero_raises_error(self):
        """Test that port 0 raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ServerConfig(port=0)

        self.assertIn("Port must be between 1 and 65535", str(context.exception))

    def test_port_negative_raises_error(self):
        """Test that negative port raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ServerConfig(port=-1)

        self.assertIn("Port must be between 1 and 65535", str(context.exception))

    def test_port_above_maximum_raises_error(self):
        """Test that port above 65535 raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ServerConfig(port=65536)

        self.assertIn("Port must be between 1 and 65535", str(context.exception))

    def test_port_large_value_raises_error(self):
        """Test that very large port raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ServerConfig(port=100000)

        self.assertIn("Port must be between 1 and 65535", str(context.exception))

    def test_port_invalid_type_raises_error(self):
        """Test that non-integer port raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ServerConfig(port="not_an_int")

        self.assertIn("Port must be an integer", str(context.exception))

    def test_port_float_raises_error(self):
        """Test that float port raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ServerConfig(port=5000.5)

        self.assertIn("Port must be an integer", str(context.exception))

    def test_multiple_valid_parameters(self):
        """Test ServerConfig with multiple valid parameters."""
        config = ServerConfig(host="127.0.0.1", port=8080)

        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, 8080)

    def test_repr(self):
        """Test string representation of ServerConfig."""
        config = ServerConfig(host="localhost", port=5000)

        repr_str = repr(config)

        self.assertIn("ServerConfig", repr_str)
        self.assertIn("host=", repr_str)
        self.assertIn("localhost", repr_str)
        self.assertIn("port=", repr_str)
        self.assertIn("5000", repr_str)

    def test_repr_with_none_values(self):
        """Test repr with None values."""
        config = ServerConfig(host=None, port=None)

        repr_str = repr(config)

        self.assertIn("ServerConfig", repr_str)
        self.assertIn("None", repr_str)

    def test_getitem_access(self):
        """Test dictionary-style access via __getitem__."""
        config = ServerConfig(host="localhost", port=8080)

        self.assertEqual(config["host"], "localhost")
        self.assertEqual(config["port"], 8080)

    def test_getitem_with_missing_attribute(self):
        """Test __getitem__ raises KeyError for missing attributes."""
        config = ServerConfig()

        with self.assertRaises(KeyError):
            _ = config["nonexistent"]

    def test_inherits_from_base_section_config(self):
        """Test that ServerConfig inherits from BaseConfig."""
        from data_exchange_agent.config.sections.base_section_config import BaseSectionConfig

        config = ServerConfig()

        self.assertIsInstance(config, BaseSectionConfig)

    def test_none_values_pass_validation(self):
        """Test that None values don't trigger validation errors."""
        # This should not raise any errors
        config = ServerConfig(host=None, port=None)

        self.assertIsNone(config.host)
        self.assertIsNone(config.port)

    def test_has_required_fields_attribute(self):
        """Test that ServerConfig has _required_fields attribute."""
        config = ServerConfig()

        self.assertTrue(hasattr(config, "_required_fields"))
        self.assertIsInstance(config._required_fields, list)

    def test_default_required_fields_is_empty(self):
        """Test that default _required_fields is empty."""
        self.assertEqual(ServerConfig._required_fields, [])


class TestServerConfigEdgeCases(unittest.TestCase):
    """Test edge cases for ServerConfig."""

    def test_host_empty_string(self):
        """Test host with empty string (should be invalid if validated)."""
        # Note: Current implementation allows empty string if host is not None
        config = ServerConfig(host="")
        self.assertEqual(config.host, "")

    def test_host_with_whitespace(self):
        """Test host with whitespace."""
        config = ServerConfig(host="   ")
        self.assertEqual(config.host, "   ")

    def test_port_boundary_value_1(self):
        """Test port at lower boundary (1)."""
        config = ServerConfig(port=1)
        self.assertEqual(config.port, 1)

    def test_port_boundary_value_65535(self):
        """Test port at upper boundary (65535)."""
        config = ServerConfig(port=65535)
        self.assertEqual(config.port, 65535)

    def test_multiple_invalid_parameters(self):
        """Test that first invalid parameter is reported."""
        with self.assertRaises(ValueError):
            ServerConfig(host=123, port="invalid")

    def test_attribute_modification_after_creation(self):
        """Test that attributes can be modified after creation."""
        config = ServerConfig(host="localhost", port=5000)

        # Modify the attributes (note: this bypasses validation)
        config.host = "127.0.0.1"
        config.port = 8080

        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, 8080)

    def test_host_with_ipv6(self):
        """Test host with IPv6 address."""
        config = ServerConfig(host="::1")

        self.assertEqual(config.host, "::1")

    def test_host_with_full_ipv6(self):
        """Test host with full IPv6 address."""
        config = ServerConfig(host="2001:0db8:85a3:0000:0000:8a2e:0370:7334")

        self.assertEqual(config.host, "2001:0db8:85a3:0000:0000:8a2e:0370:7334")

    def test_host_with_port_in_string_not_parsed(self):
        """Test that host with port notation is not parsed."""
        # The host can contain colon (like IPv6 or host:port notation)
        # but ServerConfig doesn't parse it - it's just a string
        config = ServerConfig(host="localhost:8080", port=5000)

        self.assertEqual(config.host, "localhost:8080")
        self.assertEqual(config.port, 5000)


if __name__ == "__main__":
    unittest.main()
