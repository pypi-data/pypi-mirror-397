"""
Unit tests for BaseJDBCConnectionConfig base class.

This module tests the abstract base class for JDBC connection configurations,
including validation, URL building, and field representation.
"""

import unittest

from parameterized import parameterized

from data_exchange_agent.config.sections.connections.jdbc.base import BaseJDBCConnectionConfig


class ConcreteJDBCConnectionConfig(BaseJDBCConnectionConfig):
    """Concrete implementation of BaseJDBCConnectionConfig for testing."""

    def build_url(self) -> str:
        """Build a simple test JDBC URL."""
        return f"jdbc:test://{self.host}:{self.port}/{self.database}"


class TestJDBCConnectionConfig(unittest.TestCase):
    """Test suite for BaseJDBCConnectionConfig class."""

    def test_initialization(self):
        """Test BaseJDBCConnectionConfig initialization with required fields."""
        config = ConcreteJDBCConnectionConfig(
            driver_name="test_driver",
            username="test_user",
            password="test_pass",
            database="test_db",
            host="localhost",
            port=5432,
        )

        self.assertEqual(config.driver_name, "test_driver")
        self.assertEqual(config.username, "test_user")
        self.assertEqual(config.password, "test_pass")
        self.assertEqual(config.database, "test_db")
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 5432)
        self.assertEqual(config.extra_options, {})
        self.assertEqual(config.url, "jdbc:test://localhost:5432/test_db")

    def test_initialization_with_extra_options(self):
        """Test BaseJDBCConnectionConfig initialization with extra options."""
        config = ConcreteJDBCConnectionConfig(
            driver_name="test_driver",
            username="test_user",
            password="test_pass",
            database="test_db",
            host="localhost",
            port=5432,
            ssl=True,
            timeout=30,
            application_name="test_app",
        )

        self.assertEqual(config.extra_options["ssl"], True)
        self.assertEqual(config.extra_options["timeout"], 30)
        self.assertEqual(config.extra_options["application_name"], "test_app")

    def test_build_url_called_during_init(self):
        """Test that build_url is called during BaseJDBCConnectionConfig initialization."""
        config = ConcreteJDBCConnectionConfig(
            driver_name="test_driver",
            username="test_user",
            password="test_pass",
            database="test_db",
            host="192.168.1.1",
            port=3306,
        )

        self.assertEqual(config.url, "jdbc:test://192.168.1.1:3306/test_db")

    def test_repr_fields_masks_password(self):
        """Test that _repr_fields masks the password."""
        config = ConcreteJDBCConnectionConfig(
            driver_name="test_driver",
            username="test_user",
            password="fake_test_password",  # ggshield:ignore - test data only
            database="test_db",
            host="localhost",
            port=5432,
        )

        repr_fields = config._repr_fields()

        self.assertIn("password='***'", repr_fields)
        self.assertNotIn("fake_test_password", repr_fields)

    def test_repr_fields_masks_sensitive_extra_options(self):
        """Test that _repr_fields masks sensitive data in extra_options."""
        config = ConcreteJDBCConnectionConfig(
            driver_name="test_driver",
            username="test_user",
            password="fake_extra_password",  # ggshield:ignore - test data only
            database="test_db",
            host="localhost",
            port=5432,
            api_key="fake_test_key",  # ggshield:ignore - test data only
        )

        repr_fields = config._repr_fields()

        self.assertIn("password='***'", repr_fields)
        self.assertNotIn("fake_extra_password", repr_fields)
        self.assertNotIn("fake_test_key", repr_fields)

    def test_repr_fields_includes_all_fields(self):
        """Test that _repr_fields includes all expected fields."""
        config = ConcreteJDBCConnectionConfig(
            driver_name="test_driver",
            username="test_user",
            password="test_pass",
            database="test_db",
            host="localhost",
            port=5432,
        )

        repr_fields = config._repr_fields()

        self.assertIn("driver_name='test_driver'", repr_fields)
        self.assertIn("username='test_user'", repr_fields)
        self.assertIn("host='localhost'", repr_fields)
        self.assertIn("port=5432", repr_fields)
        self.assertIn("database='test_db'", repr_fields)

    def test_required_fields_attribute(self):
        """Test that _required_fields attribute is defined."""
        self.assertIn("driver_name", BaseJDBCConnectionConfig._required_fields)
        self.assertIn("username", BaseJDBCConnectionConfig._required_fields)
        self.assertIn("password", BaseJDBCConnectionConfig._required_fields)
        self.assertIn("database", BaseJDBCConnectionConfig._required_fields)
        self.assertIn("host", BaseJDBCConnectionConfig._required_fields)
        self.assertIn("port", BaseJDBCConnectionConfig._required_fields)
        self.assertIn("url", BaseJDBCConnectionConfig._required_fields)

    def test_dns_pattern_validation(self):
        """Test DNS pattern validation regex."""
        # Valid DNS names
        self.assertIsNotNone(BaseJDBCConnectionConfig._HOST_DNS_PATTERN.match("localhost"))
        self.assertIsNotNone(BaseJDBCConnectionConfig._HOST_DNS_PATTERN.match("example.com"))
        self.assertIsNotNone(BaseJDBCConnectionConfig._HOST_DNS_PATTERN.match("sub.example.com"))
        self.assertIsNotNone(BaseJDBCConnectionConfig._HOST_DNS_PATTERN.match("my-host.example.com"))
        self.assertIsNotNone(BaseJDBCConnectionConfig._HOST_DNS_PATTERN.match("non_rfc_but_still_valid"))

        # Invalid DNS names
        self.assertIsNone(BaseJDBCConnectionConfig._HOST_DNS_PATTERN.match("host with spaces"))

    def test_ip_pattern_validation(self):
        """Test IP pattern validation regex."""
        # Valid IP addresses (format-wise)
        self.assertIsNotNone(BaseJDBCConnectionConfig._HOST_IP_PATTERN.match("192.168.1.1"))
        self.assertIsNotNone(BaseJDBCConnectionConfig._HOST_IP_PATTERN.match("10.0.0.1"))
        self.assertIsNotNone(BaseJDBCConnectionConfig._HOST_IP_PATTERN.match("127.0.0.1"))

        # Invalid IP addresses
        self.assertIsNone(BaseJDBCConnectionConfig._HOST_IP_PATTERN.match("localhost"))
        self.assertIsNone(BaseJDBCConnectionConfig._HOST_IP_PATTERN.match("192.168.1"))
        self.assertIsNone(BaseJDBCConnectionConfig._HOST_IP_PATTERN.match("not.an.ip.address"))

    def test_different_port_numbers(self):
        """Test initialization with different port numbers."""
        config_postgres = ConcreteJDBCConnectionConfig(
            driver_name="postgresql",
            username="user",
            password="pass",
            database="db",
            host="localhost",
            port=5432,
        )

        config_mysql = ConcreteJDBCConnectionConfig(
            driver_name="mysql",
            username="user",
            password="pass",
            database="db",
            host="localhost",
            port=3306,
        )

        self.assertEqual(config_postgres.port, 5432)
        self.assertEqual(config_mysql.port, 3306)

    def test_extra_options_with_various_types(self):
        """Test extra_options with different data types."""
        config = ConcreteJDBCConnectionConfig(
            driver_name="test_driver",
            username="test_user",
            password="test_pass",
            database="test_db",
            host="localhost",
            port=5432,
            ssl=True,
            timeout=30,
            max_connections=100,
            retry_delay=1.5,
        )

        self.assertIsInstance(config.extra_options["ssl"], bool)
        self.assertIsInstance(config.extra_options["timeout"], int)
        self.assertIsInstance(config.extra_options["max_connections"], int)
        self.assertIsInstance(config.extra_options["retry_delay"], float)


class TestJDBCConnectionConfigExtraOptions(unittest.TestCase):
    """Test extra options for PostgreSQL."""

    @parameterized.expand(
        [
            ("trueOption", True),
            ("falseOption", False),
            ("integerOption", 1234567890),
            ("floatOption", 1234567890.1234567890),
            ("stringOption", "test_string"),
            ("leading_trailing_whitespace_option", "  value  "),
            ("special_characters_option", "value with spaces & symbols!"),
            ("  key_with_leading_trailing_whitespace  ", "value"),
            ("  key with spaces & symbols!  ", "value"),
        ]
    )
    def test_valid_extra_option_values(self, option_name, option_value):
        """Test valid extra option values do not raise ValueError."""
        config = ConcreteJDBCConnectionConfig(
            driver_name="test_driver",
            username="test_user",
            password="test_pass",
            database="test_db",
            host="localhost",
            port=5432,
            **{option_name: option_value},
        )

        self.assertEqual(config.extra_options[option_name], option_value)

    @parameterized.expand(
        [
            ("emptyOption", ""),
            ("whitespaceOption", "   "),
            ("noneOption", None),
            ("", "value"),
            ("  ", "value"),
        ]
    )
    def test_invalid_extra_option_values(self, option_name, option_value):
        """Test invalid extra option values raise ValueError."""
        with self.assertRaises(ValueError) as context:
            _ = ConcreteJDBCConnectionConfig(
                driver_name="test_driver",
                username="test_user",
                password="test_pass",
                database="test_db",
                host="localhost",
                port=5432,
                **{option_name: option_value},
            )

        validation_error = str(context.exception)
        self.assertNotEqual(validation_error.strip(), "")


class TestJDBCConnectionConfigEdgeCases(unittest.TestCase):
    """Test edge cases and error handling in BaseJDBCConnectionConfig."""

    def test_empty_extra_options(self):
        """Test initialization with no extra options."""
        config = ConcreteJDBCConnectionConfig(
            driver_name="test_driver",
            username="test_user",
            password="test_pass",
            database="test_db",
            host="localhost",
            port=5432,
        )

        self.assertEqual(config.extra_options, {})

    def test_empty_extra_option_keys_are_invalid(self):
        """Test that empty extra option keys are invalid."""
        with self.assertRaises(ValueError) as context:
            _ = ConcreteJDBCConnectionConfig(
                driver_name="test_driver",
                username="test_user",
                password="test_pass",
                database="test_db",
                host="localhost",
                port=5432,
                **{"": "value"},
            )

        validation_error = str(context.exception)
        self.assertIsNotNone(validation_error)
        self.assertIn("cannot be empty", validation_error)

    def test_whitespace_only_extra_option_keys_are_invalid(self):
        """Test that whitespace-only extra option keys are invalid."""
        with self.assertRaises(ValueError) as context:
            _ = ConcreteJDBCConnectionConfig(
                driver_name="test_driver",
                username="test_user",
                password="test_pass",
                database="test_db",
                host="localhost",
                port=5432,
                **{"   ": "value"},
            )

        validation_error = str(context.exception)
        self.assertIsNotNone(validation_error)
        self.assertIn("cannot contain only whitespace", validation_error)

    def test_empty_extra_option_values_are_invalid(self):
        """Test that empty extra option values are invalid."""
        with self.assertRaises(ValueError) as context:
            _ = ConcreteJDBCConnectionConfig(
                driver_name="test_driver",
                username="test_user",
                password="test_pass",
                database="test_db",
                host="localhost",
                port=5432,
                empty_option="",
            )

        validation_error = str(context.exception)
        self.assertIsNotNone(validation_error)
        self.assertIn("cannot be empty", validation_error)

    def test_whitespace_only_extra_option_values_are_invalid(self):
        """Test that whitespace-only extra option values are invalid."""
        with self.assertRaises(ValueError) as context:
            _ = ConcreteJDBCConnectionConfig(
                driver_name="test_driver",
                username="test_user",
                password="test_pass",
                database="test_db",
                host="localhost",
                port=5432,
                whitespace_option="   ",
            )

        validation_error = str(context.exception)
        self.assertIsNotNone(validation_error)
        self.assertIn("cannot contain only whitespace", validation_error)

    def test_special_characters_in_fields(self):
        """Test handling of special characters in fields."""
        config = ConcreteJDBCConnectionConfig(
            driver_name="test_driver",
            username="user@domain",
            password="fake_test_password_123",  # ggshield:ignore - test data only
            database="test-db_123",
            host="host-name.example.com",
            port=5432,
        )

        self.assertEqual(config.username, "user@domain")
        self.assertEqual(config.password, "fake_test_password_123")
        self.assertEqual(config.database, "test-db_123")

    def test_numeric_string_in_extra_options(self):
        """Test extra_options with numeric strings."""
        config = ConcreteJDBCConnectionConfig(
            driver_name="test_driver",
            username="test_user",
            password="test_pass",
            database="test_db",
            host="localhost",
            port=5432,
            version="1.0",
        )

        self.assertEqual(config.extra_options["version"], "1.0")

    def test_ipv4_host(self):
        """Test initialization with IPv4 address as host."""
        config = ConcreteJDBCConnectionConfig(
            driver_name="test_driver",
            username="test_user",
            password="test_pass",
            database="test_db",
            host="192.168.1.100",
            port=5432,
        )

        self.assertEqual(config.host, "192.168.1.100")
        self.assertIn("192.168.1.100", config.url)


if __name__ == "__main__":
    unittest.main()
