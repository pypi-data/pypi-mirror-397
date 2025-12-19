"""
Comprehensive test suite for the DataSourceRegistry class.

This test class validates the registry pattern implementation for data sources,
including registration, retrieval, and creation of data source instances.
"""

import unittest

from unittest.mock import Mock, patch

from data_exchange_agent.constants.data_source_types import DataSourceType
from data_exchange_agent.data_sources.base import BaseDataSource
from data_exchange_agent.data_sources.data_source_registry import DataSourceRegistry
from data_exchange_agent.utils.base_registry import BaseRegistry


class TestDataSourceRegistry(unittest.TestCase):
    """
    Test suite for the DataSourceRegistry class.

    Validates that DataSourceRegistry correctly implements the registry pattern
    for managing data source classes.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Store the original registry to restore after tests
        self.original_registry = DataSourceRegistry._registry.copy()

    def tearDown(self):
        """Restore the original registry after each test."""
        DataSourceRegistry._registry = self.original_registry

    def test_data_source_registry_extends_base_registry(self):
        """Test that DataSourceRegistry extends BaseRegistry."""
        self.assertTrue(issubclass(DataSourceRegistry, BaseRegistry))

    def test_registry_type_name_is_data_source(self):
        """Test that registry type name is 'data source'."""
        self.assertEqual(DataSourceRegistry._registry_type_name, "data source")

    def test_register_data_source(self):
        """Test registering a new data source class."""
        mock_class = Mock
        DataSourceRegistry.register("test_source", mock_class)

        self.assertIn("test_source", DataSourceRegistry._registry)
        self.assertEqual(DataSourceRegistry._registry["test_source"], mock_class)

    def test_get_registered_data_source(self):
        """Test getting a registered data source class."""
        mock_class = Mock
        DataSourceRegistry.register("test_source", mock_class)

        result = DataSourceRegistry.get("test_source")

        self.assertEqual(result, mock_class)

    def test_get_unregistered_data_source_raises_key_error(self):
        """Test that getting an unregistered data source raises KeyError."""
        with self.assertRaises(KeyError) as context:
            DataSourceRegistry.get("nonexistent_source")

        error_message = str(context.exception)
        self.assertIn("Data source", error_message)
        self.assertIn("not registered", error_message)

    def test_create_data_source_instance(self):
        """Test creating an instance of a registered data source."""

        class MockDataSource(BaseDataSource):
            def __init__(self, **kwargs):
                self.kwargs = kwargs

            @property
            def statement(self) -> str:
                return "SELECT * FROM test"

            @property
            def results_folder_path(self) -> str:
                return "/tmp/results"

            @property
            def base_file_name(self) -> str:
                return "result"

            def export_data(self) -> bool:
                return True

        DataSourceRegistry.register("mock_source", MockDataSource)

        instance = DataSourceRegistry.create("mock_source", param1="value1", param2="value2")

        self.assertIsInstance(instance, MockDataSource)
        self.assertEqual(instance.kwargs["param1"], "value1")
        self.assertEqual(instance.kwargs["param2"], "value2")

    def test_create_with_unregistered_source_raises_key_error(self):
        """Test that creating an unregistered data source raises KeyError."""
        with self.assertRaises(KeyError) as context:
            DataSourceRegistry.create("nonexistent_source")

        error_message = str(context.exception)
        self.assertIn("Data source", error_message)
        self.assertIn("not registered", error_message)

    def test_list_types_returns_registered_types(self):
        """Test that list_types returns all registered type names."""
        DataSourceRegistry._registry = {}  # Clear registry for test
        DataSourceRegistry.register("source_a", Mock)
        DataSourceRegistry.register("source_b", Mock)

        types = DataSourceRegistry.list_types()

        self.assertEqual(sorted(types), ["source_a", "source_b"])

    def test_is_registered_returns_true_for_registered(self):
        """Test that is_registered returns True for registered sources."""
        DataSourceRegistry.register("test_source", Mock)

        self.assertTrue(DataSourceRegistry.is_registered("test_source"))

    def test_is_registered_returns_false_for_unregistered(self):
        """Test that is_registered returns False for unregistered sources."""
        self.assertFalse(DataSourceRegistry.is_registered("nonexistent_source"))

    def test_register_overwrites_existing(self):
        """Test that registering with same name overwrites existing."""
        mock_class_1 = Mock
        mock_class_2 = Mock

        DataSourceRegistry.register("test_source", mock_class_1)
        DataSourceRegistry.register("test_source", mock_class_2)

        result = DataSourceRegistry.get("test_source")
        self.assertEqual(result, mock_class_2)

    def test_registry_is_isolated_per_subclass(self):
        """Test that each subclass has its own isolated registry."""
        # DataSourceRegistry should have its own registry separate from BaseRegistry

        class AnotherRegistry(BaseRegistry[BaseDataSource]):
            _registry_type_name = "another"

        AnotherRegistry.register("another_source", Mock)

        # Verify DataSourceRegistry doesn't have the "another_source"
        self.assertFalse(DataSourceRegistry.is_registered("another_source"))


class TestDataSourceRegistryIntegration(unittest.TestCase):
    """
    Integration tests for DataSourceRegistry with actual data source types.

    Validates that the registry works correctly with actual data source
    implementations and enum types.
    """

    def test_jdbc_data_source_is_registered(self):
        """Test that JDBCDataSource is registered by default."""
        # The __init__.py of data_sources should register JDBCDataSource
        self.assertTrue(DataSourceRegistry.is_registered(DataSourceType.JDBC))

    def test_get_jdbc_data_source_class(self):
        """Test getting the JDBCDataSource class from registry."""
        from data_exchange_agent.data_sources.jdbc_data_source import JDBCDataSource

        result = DataSourceRegistry.get(DataSourceType.JDBC)

        self.assertEqual(result, JDBCDataSource)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    def test_create_jdbc_data_source_instance(self, mock_jdbc_jar_dict_class):
        """Test creating a JDBCDataSource instance through the registry."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_logger = Mock()

        auth_info = {
            "driver_name": "postgresql",
            "url": "jdbc:postgresql://localhost:5432/testdb",
            "username": "testuser",
            "password": "testpass",
        }

        from data_exchange_agent.data_sources.jdbc_data_source import JDBCDataSource

        instance = DataSourceRegistry.create(
            DataSourceType.JDBC,
            source_authentication_info=auth_info,
            statement="SELECT * FROM users",
            results_folder_path="/tmp/results",
            logger=mock_logger,
        )

        self.assertIsInstance(instance, JDBCDataSource)
        self.assertEqual(instance.statement, "SELECT * FROM users")

    def test_list_types_includes_jdbc(self):
        """Test that list_types includes JDBC type."""
        types = DataSourceRegistry.list_types()

        self.assertIn(DataSourceType.JDBC, types)


class TestDataSourceRegistryErrorMessages(unittest.TestCase):
    """
    Test suite for error messages from DataSourceRegistry.

    Validates that error messages are clear and helpful.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.original_registry = DataSourceRegistry._registry.copy()

    def tearDown(self):
        """Restore the original registry after each test."""
        DataSourceRegistry._registry = self.original_registry

    def test_error_message_includes_available_types(self):
        """Test that error message includes available types when getting nonexistent."""
        DataSourceRegistry._registry = {"type_a": Mock, "type_b": Mock}

        with self.assertRaises(KeyError) as context:
            DataSourceRegistry.get("nonexistent")

        error_message = str(context.exception)
        self.assertIn("type_a", error_message)
        self.assertIn("type_b", error_message)

    def test_error_message_when_no_types_registered(self):
        """Test error message when no types are registered."""
        DataSourceRegistry._registry = {}

        with self.assertRaises(KeyError) as context:
            DataSourceRegistry.get("nonexistent")

        error_message = str(context.exception)
        self.assertIn("none", error_message.lower())


if __name__ == "__main__":
    unittest.main()
