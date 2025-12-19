"""
Unit tests for PostgreSQLConnectionConfig class.

This module tests the PostgreSQL-specific JDBC connection configuration,
including URL building, query parameter handling, and validation.
"""

import unittest

from urllib.parse import quote

from parameterized import parameterized

from data_exchange_agent.config.sections.connections.jdbc.postgresql import PostgreSQLConnectionConfig
from data_exchange_agent.constants.connection_types import ConnectionType


TEST_USER = "test_user"
TEST_PASS = "test_pass"  # ggshield:ignore
TEST_DB = "test_db"
TEST_HOST = "localhost"
TEST_PORT = 5432


class TestPostgreSQLConnectionConfig(unittest.TestCase):
    """Test suite for PostgreSQLConnectionConfig class."""

    def test_initialization(self):
        """Test PostgreSQLConnectionConfig initialization with required fields."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            host=TEST_HOST,
            port=TEST_PORT,
        )

        self.assertEqual(config.driver_name, ConnectionType.POSTGRESQL)
        self.assertEqual(config.username, TEST_USER)
        self.assertEqual(config.password, TEST_PASS)
        self.assertEqual(config.database, TEST_DB)
        self.assertEqual(config.host, TEST_HOST)
        self.assertEqual(config.port, TEST_PORT)
        self.assertEqual(config.extra_options, {})

    def test_default_values(self):
        """Test PostgreSQLConnectionConfig uses default values."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
        )

        self.assertEqual(config.host, TEST_HOST)
        self.assertEqual(config.port, TEST_PORT)

    def test_repr_fields_includes_all_fields(self):
        """Test that _repr_fields includes all expected fields."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            host=TEST_HOST,
            port=TEST_PORT,
        )

        repr_fields = config._repr_fields()

        self.assertIn("driver_name='postgresql'", repr_fields)
        self.assertIn(f"username='{TEST_USER}'", repr_fields)
        self.assertIn("password='***'", repr_fields)
        self.assertIn(f"host='{TEST_HOST}'", repr_fields)
        self.assertIn(f"port={TEST_PORT}", repr_fields)
        self.assertIn(f"database='{TEST_DB}'", repr_fields)

    def test_password_is_masked_in_repr(self):
        """Test that password is masked in string representation."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password="secret_password_123",  # ggshield:ignore - test data only
            database=TEST_DB,
        )

        repr_fields = config._repr_fields()
        self.assertIn("password='***'", repr_fields)
        self.assertNotIn("secret_password_123", repr_fields)


class TestPostgreSQLConnectionConfigURLFormatting(unittest.TestCase):
    """Test URL formatting for PostgreSQL."""

    def test_url_with_single_option_starts_with_question_mark(self):
        """Test that query string starts with ? when options exist."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            ssl=True,
        )

        url = config.url
        question_mark_count = url.count("?")
        self.assertEqual(question_mark_count, 1)
        self.assertNotIn("&", url)

    def test_url_with_multiple_options_separated_by_ampersand(self):
        """Test that multiple options are separated by &."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            ssl=True,
            sslmode="require",
            connectTimeout=10,
        )

        url = config.url

        # Count ampersands - should have exactly 2 for 3 options
        ampersand_count = url.count("&")
        self.assertEqual(ampersand_count, 2)

        # Should have exactly 1 question mark
        question_mark_count = url.count("?")
        self.assertEqual(question_mark_count, 1)

    def test_url_without_options(self):
        """Test URL building without extra options."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            host="postgres.example.com",
            port=TEST_PORT,
        )

        expected_url = f"jdbc:postgresql://postgres.example.com:{TEST_PORT}/{TEST_DB}"
        self.assertEqual(config.url, expected_url)

    def test_url_with_ipv4_host(self):
        """Test URL building with IPv4 address as host."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            host="192.168.1.100",
            port=TEST_PORT,
        )

        expected_url = f"jdbc:postgresql://192.168.1.100:{TEST_PORT}/{TEST_DB}"
        self.assertEqual(config.url, expected_url)

    def test_url_with_custom_port(self):
        """Test URL building with custom port."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            host=TEST_HOST,
            port=5433,
        )

        expected_url = f"jdbc:postgresql://localhost:5433/{TEST_DB}"
        self.assertEqual(config.url, expected_url)

    def test_url_with_special_characters_is_encoded(self):
        """Test that special characters in URL are encoded."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            host=TEST_HOST,
            port=TEST_PORT,
            applicationName="My App & Co.",
        )

        url = config.url
        # The ampersand and space should be URL encoded
        self.assertIn("applicationName=My%20App%20%26%20Co.", url)

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
    def test_url_with_valid_extra_option_values(self, option_name, option_value):
        """Test valid extra option values are included in the URL."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            **{option_name: option_value},
        )

        url = config.url
        self.assertIn(f"{quote(option_name.strip())}={quote(str(option_value).strip())}", url)


class TestPostgreSQLConnectionConfigEdgeCases(unittest.TestCase):
    """Test edge cases for PostgreSQLConnectionConfig."""

    def test_special_characters_in_database_name(self):
        """Test configuration with special characters in database name."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database="test-db_123",
            host=TEST_HOST,
            port=TEST_PORT,
        )

        self.assertIn("/test-db_123", config.url)

    def test_special_characters_in_username(self):
        """Test configuration with special characters in username."""
        config = PostgreSQLConnectionConfig(
            username="user@domain.com",
            password=TEST_PASS,
            database=TEST_DB,
        )

        self.assertEqual(config.username, "user@domain.com")

    def test_numeric_string_option_values(self):
        """Test that numeric strings are properly handled."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            prepareThreshold="5",
        )

        url = config.url
        self.assertIn("prepareThreshold=5", url)

    def test_option_with_equals_sign_in_value(self):
        """Test option value containing equals sign is properly encoded."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            options="key=value",
        )

        url = config.url
        # The equals sign in the value should be URL encoded
        self.assertIn("options=key%3Dvalue", url)

    def test_option_with_special_url_characters(self):
        """Test option values with special URL characters are encoded."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            param="value with spaces & symbols!",
        )

        url = config.url
        # Spaces and special characters should be encoded
        self.assertIn("param=value%20with%20spaces%20%26%20symbols%21", url)

    def test_very_long_database_name(self):
        """Test configuration with very long database name."""
        long_db_name = "a" * 100
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=long_db_name,
        )

        self.assertIn(f"/{long_db_name}", config.url)

    def test_many_extra_options(self):
        """Test configuration with many extra options."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            ssl=True,
            sslmode="require",
            connectTimeout=30,
            socketTimeout=60,
            loginTimeout=10,
            applicationName="TestApp",
            currentSchema="public",
            loadBalanceHosts=True,
            prepareThreshold=5,
            binaryTransfer=True,
        )

        url = config.url
        # Verify some of the options are present
        self.assertIn("ssl=True", url)
        self.assertIn("sslmode=require", url)
        self.assertIn("connectTimeout=30", url)
        self.assertIn("applicationName=TestApp", url)


class TestPostgreSQLConnectionConfigRegistration(unittest.TestCase):
    """Test PostgreSQLConnectionConfig registration in ConnectionRegistry."""

    def test_postgresql_registered_in_connection_registry(self):
        """Test that PostgreSQL connection type is registered."""
        from data_exchange_agent.config.sections.connections.connection_registry import ConnectionRegistry

        # Verify the connection type is registered
        registered_class = ConnectionRegistry.get(ConnectionType.POSTGRESQL)
        self.assertEqual(registered_class, PostgreSQLConnectionConfig)

    def test_can_create_postgresql_from_registry(self):
        """Test that PostgreSQL connection can be created from registry."""
        from data_exchange_agent.config.sections.connections.connection_registry import ConnectionRegistry

        # Get the class from registry and create an instance
        connection_class = ConnectionRegistry.get(ConnectionType.POSTGRESQL)
        config = connection_class(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
        )

        self.assertIsInstance(config, PostgreSQLConnectionConfig)
        self.assertEqual(config.driver_name, ConnectionType.POSTGRESQL)


class TestPostgreSQLConnectionConfigComparison(unittest.TestCase):
    """Test PostgreSQL configuration against base JDBC config behavior."""

    def test_inherits_from_base_jdbc_config(self):
        """Test that PostgreSQLConnectionConfig inherits from BaseJDBCConnectionConfig."""
        from data_exchange_agent.config.sections.connections.jdbc.base import BaseJDBCConnectionConfig

        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
        )

        self.assertIsInstance(config, BaseJDBCConnectionConfig)

    def test_url_is_built_during_initialization(self):
        """Test that URL is built automatically during initialization."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
        )

        # URL should be available immediately after initialization
        self.assertIsNotNone(config.url)
        self.assertTrue(config.url.startswith("jdbc:postgresql://"))

    def test_extra_options_stored_correctly(self):
        """Test that extra options are stored in the extra_options dict."""
        config = PostgreSQLConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            ssl=True,
            connectTimeout=30,
        )

        self.assertIn("ssl", config.extra_options)
        self.assertIn("connectTimeout", config.extra_options)
        self.assertEqual(config.extra_options["ssl"], True)
        self.assertEqual(config.extra_options["connectTimeout"], 30)


if __name__ == "__main__":
    unittest.main()
