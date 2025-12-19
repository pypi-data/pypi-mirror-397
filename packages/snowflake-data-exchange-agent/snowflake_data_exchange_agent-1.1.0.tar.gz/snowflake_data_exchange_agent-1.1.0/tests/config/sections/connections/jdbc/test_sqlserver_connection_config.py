"""
Unit tests for SQLServerConnectionConfig class.

This module tests the SQL Server-specific JDBC connection configuration,
including instance name handling, URL building, and validation.
"""

import unittest

from urllib.parse import quote

from parameterized import parameterized

from data_exchange_agent.config.sections.connections.jdbc.sqlserver import SQLServerConnectionConfig
from data_exchange_agent.constants.connection_types import ConnectionType


TEST_USER = "test_user"
TEST_PASS = "test_pass"  # ggshield:ignore
TEST_DB = "test_db"
TEST_HOST = "localhost"
TEST_PORT = 1433


class TestSQLServerConnectionConfig(unittest.TestCase):
    """Test suite for SQLServerConnectionConfig class."""

    def test_initialization(self):
        """Test SQLServerConnectionConfig initialization with required fields."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            host=TEST_HOST,
            port=TEST_PORT,
        )

        self.assertEqual(config.driver_name, ConnectionType.SQLSERVER)
        self.assertEqual(config.username, TEST_USER)
        self.assertEqual(config.password, TEST_PASS)
        self.assertEqual(config.database, TEST_DB)
        self.assertEqual(config.host, TEST_HOST)
        self.assertEqual(config.port, TEST_PORT)
        self.assertEqual(config.extra_options, {})

    def test_default_values(self):
        """Test SQLServerConnectionConfig uses default values."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
        )

        self.assertEqual(config.host, TEST_HOST)
        self.assertEqual(config.port, TEST_PORT)

    def test_repr_fields_includes_all_fields(self):
        """Test that _repr_fields includes all expected fields."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            host=TEST_HOST,
            port=TEST_PORT,
        )

        repr_fields = config._repr_fields()

        self.assertIn("driver_name='sqlserver'", repr_fields)
        self.assertIn(f"username='{TEST_USER}'", repr_fields)
        self.assertIn("password='***'", repr_fields)
        self.assertIn(f"host='{TEST_HOST}'", repr_fields)
        self.assertIn(f"port={TEST_PORT}", repr_fields)
        self.assertIn(f"database='{TEST_DB}'", repr_fields)

    def test_password_is_masked_in_repr(self):
        """Test that password is masked in string representation."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password="secret_password_123",  # ggshield:ignore - test data only
            database=TEST_DB,
        )

        repr_fields = config._repr_fields()
        self.assertIn("password='***'", repr_fields)
        self.assertNotIn("secret_password_123", repr_fields)


class TestSQLServerConnectionConfigURLFormatting(unittest.TestCase):
    """Test URL formatting for SQL Server."""

    def test_url_without_options_and_without_instance(self):
        """Test URL building without extra options and without instance name."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            host="sqlserver.example.com",
            port=TEST_PORT,
        )

        expected_url = f"jdbc:sqlserver://sqlserver.example.com:{TEST_PORT};databaseName={TEST_DB}"
        self.assertEqual(config.url, expected_url)

    def test_url_with_instance_name(self):
        """Test URL building with instance name."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            host="sqlserver.example.com",
            port=TEST_PORT,
            instanceName="SQLEXPRESS",
        )

        expected_url = f"jdbc:sqlserver://sqlserver.example.com\\SQLEXPRESS:{TEST_PORT};databaseName={TEST_DB}"
        self.assertEqual(config.url, expected_url)

    def test_url_with_single_option_separated_by_semicolon(self):
        """Test that options are separated by semicolons."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            encrypt=True,
        )

        url = config.url
        # Should have semicolons, not ampersands
        self.assertIn(";", url)
        self.assertNotIn("&", url)
        self.assertIn("encrypt=True", url)

    def test_url_with_multiple_options_separated_by_semicolons(self):
        """Test that multiple options are separated by semicolons."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            encrypt=True,
            trustServerCertificate=True,
            loginTimeout=30,
        )

        url = config.url
        # Count semicolons - should have at least 4 (databaseName + 3 options)
        semicolon_count = url.count(";")
        self.assertGreaterEqual(semicolon_count, 4)

        # Verify options are present
        self.assertIn("encrypt=True", url)
        self.assertIn("trustServerCertificate=True", url)
        self.assertIn("loginTimeout=30", url)

    def test_url_with_ipv4_host(self):
        """Test URL building with IPv4 address as host."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            host="192.168.1.100",
            port=TEST_PORT,
        )

        expected_url = f"jdbc:sqlserver://192.168.1.100:{TEST_PORT};databaseName={TEST_DB}"
        self.assertEqual(config.url, expected_url)

    def test_url_with_custom_port(self):
        """Test URL building with custom port."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            host=TEST_HOST,
            port=14330,
        )

        expected_url = f"jdbc:sqlserver://localhost:14330;databaseName={TEST_DB}"
        self.assertEqual(config.url, expected_url)

    def test_url_with_special_characters_is_encoded(self):
        """Test that special characters in URL are encoded."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            applicationName="My App & Co.",
        )

        url = config.url
        # The ampersand and space should be URL encoded
        self.assertIn("applicationName=My%20App%20%26%20Co.", url)

    def test_instance_name_not_included_as_separate_option(self):
        """Test that instance name doesn't appear as separate option in URL."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            instanceName="SQLEXPRESS",
            encrypt=True,
        )

        url = config.url
        # Instance name should be in the host part with backslash
        self.assertIn("\\SQLEXPRESS:", url)
        # But not as a separate ;instanceName= option
        self.assertNotIn(";instanceName=", url)

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
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            **{option_name: option_value},
        )

        url = config.url
        self.assertIn(f"{quote(option_name.strip())}={quote(str(option_value).strip())}", url)


class TestSQLServerConnectionConfigInstanceNameValidation(unittest.TestCase):
    """Test instance name validation for SQL Server."""

    @parameterized.expand(
        [
            ("SQLEXPRESS"),
            ("SQL2019"),
            ("SQL_EXPRESS"),
            ("SQL$INSTANCE"),
            ("S"),  # Minimum 1 character
            ("SQLEXPRESS123456"),  # Exactly 16 characters
            ("  SQLEXPRESS123456  "),  # Leading and trailing whitespace
        ]
    )
    def test_valid_instance_names(self, instance_name):
        """Test that valid instance names are accepted."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            instanceName=instance_name,
        )

        validation_error = config._validate_instance_name()
        self.assertIsNone(validation_error)

    @parameterized.expand(
        [
            ("2SQL", "must start with a letter"),
            ("SQL-EXPRESS", "only contain alphanumeric characters, underscores (_), and dollar signs ($)"),
            ("SQL EXPRESS", "only contain alphanumeric characters, underscores (_), and dollar signs ($)"),
            ("VERYLONGINSTANCENAME", "length must be less than or equal to 16"),
            (123, "must be a string"),
            ("", "cannot be empty"),
            ("    ", "cannot contain only whitespace"),
        ]
    )
    def test_invalid_instance_names(self, instance_name, expected_error_fragment):
        """Test that invalid instance names raise ValueError."""
        with self.assertRaises(ValueError) as context:
            SQLServerConnectionConfig(
                username=TEST_USER,
                password=TEST_PASS,
                database=TEST_DB,
                instanceName=instance_name,
            )

        validation_error = str(context.exception)
        self.assertIn(expected_error_fragment, validation_error)

    def test_instance_name_validation_without_instance_name(self):
        """Test validation passes when no instance name is provided."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
        )

        validation_error = config._validate_instance_name()
        self.assertIsNone(validation_error)


class TestSQLServerConnectionConfigEdgeCases(unittest.TestCase):
    """Test edge cases for SQLServerConnectionConfig."""

    def test_special_characters_in_database_name(self):
        """Test configuration with special characters in database name."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database="test-db_123",
            host=TEST_HOST,
            port=TEST_PORT,
        )

        self.assertIn("databaseName=test-db_123", config.url)

    def test_special_characters_in_username(self):
        """Test configuration with special characters in username."""
        config = SQLServerConnectionConfig(
            username="user@domain.com",
            password=TEST_PASS,
            database=TEST_DB,
        )

        self.assertEqual(config.username, "user@domain.com")

    def test_option_with_equals_sign_in_value(self):
        """Test option value containing equals sign is properly encoded."""
        config = SQLServerConnectionConfig(
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
        config = SQLServerConnectionConfig(
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
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=long_db_name,
        )

        self.assertIn(f"databaseName={long_db_name}", config.url)

    def test_many_extra_options(self):
        """Test configuration with many extra options."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            encrypt=True,
            trustServerCertificate=True,
            loginTimeout=30,
            socketTimeout=60,
            applicationName="TestApp",
            workstationID="WS123",
            selectMethod="cursor",
            responseBuffering="adaptive",
            packetSize=8000,
        )

        url = config.url
        # Verify some of the options are present
        self.assertIn("encrypt=True", url)
        self.assertIn("trustServerCertificate=True", url)
        self.assertIn("loginTimeout=30", url)
        self.assertIn("applicationName=TestApp", url)

    def test_instance_name_and_multiple_options(self):
        """Test configuration with both instance name and multiple options."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            instanceName="SQLEXPRESS",
            encrypt=True,
            trustServerCertificate=True,
        )

        url = config.url
        # Verify instance name is in URL with backslash
        self.assertIn("\\SQLEXPRESS:", url)
        # Verify options are present
        self.assertIn("encrypt=True", url)
        self.assertIn("trustServerCertificate=True", url)
        # Verify instance name not as separate option
        self.assertNotIn(";instanceName=", url)


class TestSQLServerConnectionConfigRegistration(unittest.TestCase):
    """Test SQLServerConnectionConfig registration in ConnectionRegistry."""

    def test_sqlserver_registered_in_connection_registry(self):
        """Test that SQL Server connection type is registered."""
        from data_exchange_agent.config.sections.connections.connection_registry import ConnectionRegistry

        # Verify the connection type is registered
        registered_class = ConnectionRegistry.get(ConnectionType.SQLSERVER)
        self.assertEqual(registered_class, SQLServerConnectionConfig)

    def test_can_create_sqlserver_from_registry(self):
        """Test that SQL Server connection can be created from registry."""
        from data_exchange_agent.config.sections.connections.connection_registry import ConnectionRegistry

        # Get the class from registry and create an instance
        connection_class = ConnectionRegistry.get(ConnectionType.SQLSERVER)
        config = connection_class(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
        )

        self.assertIsInstance(config, SQLServerConnectionConfig)
        self.assertEqual(config.driver_name, ConnectionType.SQLSERVER)


class TestSQLServerConnectionConfigComparison(unittest.TestCase):
    """Test SQL Server configuration against base JDBC config behavior."""

    def test_inherits_from_base_jdbc_config(self):
        """Test that SQLServerConnectionConfig inherits from BaseJDBCConnectionConfig."""
        from data_exchange_agent.config.sections.connections.jdbc.base import BaseJDBCConnectionConfig

        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
        )

        self.assertIsInstance(config, BaseJDBCConnectionConfig)

    def test_url_is_built_during_initialization(self):
        """Test that URL is built automatically during initialization."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
        )

        # URL should be available immediately after initialization
        self.assertIsNotNone(config.url)
        self.assertTrue(config.url.startswith("jdbc:sqlserver://"))

    def test_extra_options_stored_correctly(self):
        """Test that extra options are stored in the extra_options dict."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            encrypt=True,
            loginTimeout=30,
        )

        self.assertIn("encrypt", config.extra_options)
        self.assertIn("loginTimeout", config.extra_options)
        self.assertEqual(config.extra_options["encrypt"], True)
        self.assertEqual(config.extra_options["loginTimeout"], 30)

    def test_instance_name_stored_in_extra_options(self):
        """Test that instance name is stored in extra_options."""
        config = SQLServerConnectionConfig(
            username=TEST_USER,
            password=TEST_PASS,
            database=TEST_DB,
            instanceName="SQLEXPRESS",
        )

        self.assertIn("instanceName", config.extra_options)
        self.assertEqual(config.extra_options["instanceName"], "SQLEXPRESS")


if __name__ == "__main__":
    unittest.main()
