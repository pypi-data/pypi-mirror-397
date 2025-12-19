"""
Comprehensive test suite for the JDBCDataSource class.

This test class validates the core functionality of the JDBCDataSource class,
including initialization, data export, and error handling.
"""

import os
import tempfile
import unittest

from unittest.mock import Mock, patch

from data_exchange_agent.data_sources.base import BaseDataSource
from data_exchange_agent.data_sources.jdbc_data_source import JDBCDataSource
from data_exchange_agent.data_sources.sql_command_type import SQLCommandType


class TestJDBCDataSource(unittest.TestCase):
    """
    Comprehensive test suite for the JDBCDataSource class.

    This test class validates the core functionality and ensures proper
    behavior under various conditions including normal operation,
    error scenarios, and edge cases.

    Tests use mocking where appropriate to isolate the component
    under test and ensure reliable, fast test execution.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.auth_info = {
            "driver_name": "postgresql",
            "url": "jdbc:postgresql://localhost:5432/testdb",
            "username": "testuser",
            "password": "testpass",
        }
        self.statement = "SELECT * FROM users"
        self.temp_dir = tempfile.mkdtemp()
        self.mock_logger = Mock()

    def tearDown(self):
        """Clean up after each test method."""
        # Clean up temp directory
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.build_actual_results_folder_path")
    def test_jdbc_data_source_is_base_data_source(self, mock_build_path, mock_jdbc_jar_dict_class):
        """Test that JDBCDataSource is a subclass of BaseDataSource."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict
        mock_build_path.return_value = self.temp_dir

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            logger=self.mock_logger,
        )

        self.assertIsInstance(data_source, BaseDataSource)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.build_actual_results_folder_path")
    def test_initialization_with_defaults(self, mock_build_path, mock_jdbc_jar_dict_class):
        """Test JDBCDataSource initialization with default parameters."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict
        mock_build_path.return_value = self.temp_dir

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            logger=self.mock_logger,
        )

        self.assertEqual(data_source.statement, self.statement)
        self.assertEqual(data_source.results_folder_path, self.temp_dir)
        self.assertEqual(data_source.base_file_name, "result")
        self.assertEqual(data_source.driver_name, "postgresql")
        self.assertEqual(data_source.driver_class_name, "org.postgresql.Driver")
        self.assertEqual(data_source.jar_path, "/path/to/postgresql.jar")

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    def test_initialization_with_custom_parameters(self, mock_jdbc_jar_dict_class):
        """Test JDBCDataSource initialization with custom parameters."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        custom_path = "/custom/results/path"
        custom_base_name = "custom_result"

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=custom_path,
            base_file_name=custom_base_name,
            logger=self.mock_logger,
        )

        self.assertEqual(data_source.statement, self.statement)
        self.assertEqual(data_source.results_folder_path, custom_path)
        self.assertEqual(data_source.base_file_name, custom_base_name)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    def test_initialization_with_sqlserver_driver(self, mock_jdbc_jar_dict_class):
        """Test JDBCDataSource initialization with SQL Server driver."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/mssql-jdbc.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        auth_info = {
            "driver_name": "sqlserver",
            "url": "jdbc:sqlserver://localhost:1433;databaseName=testdb",
            "username": "sa",
            "password": "password",
        }

        data_source = JDBCDataSource(
            source_authentication_info=auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        self.assertEqual(data_source.driver_name, "sqlserver")
        self.assertEqual(data_source.driver_class_name, "com.microsoft.sqlserver.jdbc.SQLServerDriver")

    @patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_success(self, mock_sql_parser, mock_jdbc_jar_dict_class, mock_jaydebeapi):
        """Test successful data export."""
        # Setup mocks
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.SELECT

        # Mock connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchmany.side_effect = [
            [(1, "Alice"), (2, "Bob")],
            [],
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_jaydebeapi.connect.return_value = mock_conn

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        result = data_source.export_data()

        self.assertTrue(result)
        mock_jaydebeapi.connect.assert_called_once()
        mock_cursor.execute.assert_called_once_with(self.statement)
        mock_conn.close.assert_called_once()

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_non_read_only_statement_raises_exception(self, mock_sql_parser, mock_jdbc_jar_dict_class):
        """Test that non-read-only statements raise an exception."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = None  # Non-read-only operation

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement="INSERT INTO users VALUES (1, 'Alice')",
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        with self.assertRaises(Exception) as context:
            data_source.export_data()

        self.assertIn("not a read-only operation", str(context.exception))

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_with_describe_statement(self, mock_sql_parser, mock_jdbc_jar_dict_class):
        """Test export_data with DESCRIBE statement."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.DESCRIBE

        with patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi") as mock_jaydebeapi:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.description = [("column_name",), ("data_type",)]
            mock_cursor.fetchmany.side_effect = [
                [("id", "INTEGER"), ("name", "VARCHAR")],
                [],
            ]
            mock_conn.cursor.return_value = mock_cursor
            mock_jaydebeapi.connect.return_value = mock_conn

            data_source = JDBCDataSource(
                source_authentication_info=self.auth_info,
                statement="DESCRIBE users",
                results_folder_path=self.temp_dir,
                logger=self.mock_logger,
            )

            result = data_source.export_data()

            self.assertTrue(result)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_with_show_statement(self, mock_sql_parser, mock_jdbc_jar_dict_class):
        """Test export_data with SHOW statement."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.SHOW

        with patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi") as mock_jaydebeapi:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.description = [("table_name",)]
            mock_cursor.fetchmany.side_effect = [
                [("users",), ("orders",)],
                [],
            ]
            mock_conn.cursor.return_value = mock_cursor
            mock_jaydebeapi.connect.return_value = mock_conn

            data_source = JDBCDataSource(
                source_authentication_info=self.auth_info,
                statement="SHOW TABLES",
                results_folder_path=self.temp_dir,
                logger=self.mock_logger,
            )

            result = data_source.export_data()

            self.assertTrue(result)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_with_explain_statement(self, mock_sql_parser, mock_jdbc_jar_dict_class):
        """Test export_data with EXPLAIN statement."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.EXPLAIN

        with patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi") as mock_jaydebeapi:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.description = [("plan",)]
            mock_cursor.fetchmany.side_effect = [
                [("Seq Scan on users",)],
                [],
            ]
            mock_conn.cursor.return_value = mock_cursor
            mock_jaydebeapi.connect.return_value = mock_conn

            data_source = JDBCDataSource(
                source_authentication_info=self.auth_info,
                statement="EXPLAIN SELECT * FROM users",
                results_folder_path=self.temp_dir,
                logger=self.mock_logger,
            )

            result = data_source.export_data()

            self.assertTrue(result)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_with_with_statement(self, mock_sql_parser, mock_jdbc_jar_dict_class):
        """Test export_data with WITH (CTE) statement."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.WITH

        with patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi") as mock_jaydebeapi:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.description = [("id",), ("name",)]
            mock_cursor.fetchmany.side_effect = [
                [(1, "Alice")],
                [],
            ]
            mock_conn.cursor.return_value = mock_cursor
            mock_jaydebeapi.connect.return_value = mock_conn

            data_source = JDBCDataSource(
                source_authentication_info=self.auth_info,
                statement="WITH cte AS (SELECT * FROM users) SELECT * FROM cte",
                results_folder_path=self.temp_dir,
                logger=self.mock_logger,
            )

            result = data_source.export_data()

            self.assertTrue(result)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_connection_error(self, mock_sql_parser, mock_jdbc_jar_dict_class, mock_jaydebeapi):
        """Test export_data handles connection errors properly."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.SELECT

        mock_jaydebeapi.connect.side_effect = Exception("Connection failed")

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        # Note: When jaydebeapi.connect() fails, the code has a bug where 'conn' is
        # not defined before the finally block, causing an UnboundLocalError.
        # This test verifies that an exception is raised in this scenario.
        with self.assertRaises(Exception) as context:
            data_source.export_data()

        self.assertIn("Connection failed", str(context.exception))

    @patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_query_execution_error(self, mock_sql_parser, mock_jdbc_jar_dict_class, mock_jaydebeapi):
        """Test export_data handles query execution errors properly."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.SELECT

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Query execution failed")
        mock_conn.cursor.return_value = mock_cursor
        mock_jaydebeapi.connect.return_value = mock_conn

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        with self.assertRaises(Exception) as context:
            data_source.export_data()

        self.assertIn("Query execution failed", str(context.exception))
        mock_conn.close.assert_called_once()

    @patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_creates_output_directory(self, mock_sql_parser, mock_jdbc_jar_dict_class, mock_jaydebeapi):
        """Test that export_data creates the output directory if it doesn't exist."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.SELECT

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [("id",)]
        mock_cursor.fetchmany.side_effect = [[(1,)], []]
        mock_conn.cursor.return_value = mock_cursor
        mock_jaydebeapi.connect.return_value = mock_conn

        # Use a path that doesn't exist
        non_existent_path = os.path.join(self.temp_dir, "new_directory")

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=non_existent_path,
            logger=self.mock_logger,
        )

        data_source.export_data()

        self.assertTrue(os.path.exists(non_existent_path))

    @patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_empty_result_set(self, mock_sql_parser, mock_jdbc_jar_dict_class, mock_jaydebeapi):
        """Test export_data handles empty result sets."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.SELECT

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchmany.return_value = []  # Empty result
        mock_conn.cursor.return_value = mock_cursor
        mock_jaydebeapi.connect.return_value = mock_conn

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        result = data_source.export_data()

        self.assertTrue(result)
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.pq.ParquetWriter")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_multiple_batches(
        self, mock_sql_parser, mock_jdbc_jar_dict_class, mock_parquet_writer, mock_jaydebeapi
    ):
        """Test export_data handles multiple batches of data."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.SELECT

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [("id",), ("name",)]
        # Simulate multiple batches
        mock_cursor.fetchmany.side_effect = [
            [(1, "Alice"), (2, "Bob")],
            [(3, "Charlie"), (4, "David")],
            [],
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_jaydebeapi.connect.return_value = mock_conn

        mock_writer_instance = Mock()
        mock_parquet_writer.return_value = mock_writer_instance

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        result = data_source.export_data()

        self.assertTrue(result)
        # Check that write_table was called for each batch
        self.assertEqual(mock_writer_instance.write_table.call_count, 2)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    def test_statement_property(self, mock_jdbc_jar_dict_class):
        """Test statement property returns the correct value."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        self.assertEqual(data_source.statement, self.statement)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    def test_results_folder_path_property(self, mock_jdbc_jar_dict_class):
        """Test results_folder_path property returns the correct value."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        self.assertEqual(data_source.results_folder_path, self.temp_dir)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    def test_base_file_name_property(self, mock_jdbc_jar_dict_class):
        """Test base_file_name property returns the correct value."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        custom_base_name = "my_result"

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            base_file_name=custom_base_name,
            logger=self.mock_logger,
        )

        self.assertEqual(data_source.base_file_name, custom_base_name)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_uses_correct_batch_size(self, mock_sql_parser, mock_jdbc_jar_dict_class, mock_jaydebeapi):
        """Test that export_data uses the correct batch size."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.SELECT

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [("id",)]
        mock_cursor.fetchmany.side_effect = [[(1,)], []]
        mock_conn.cursor.return_value = mock_cursor
        mock_jaydebeapi.connect.return_value = mock_conn

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        data_source.export_data()

        # Check that fetchmany was called with the default batch size of 50000
        mock_cursor.fetchmany.assert_any_call(50000)

    @patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_connection_closed_on_success(self, mock_sql_parser, mock_jdbc_jar_dict_class, mock_jaydebeapi):
        """Test that connection is closed after successful export."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.SELECT

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [("id",)]
        mock_cursor.fetchmany.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_jaydebeapi.connect.return_value = mock_conn

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        data_source.export_data()

        mock_conn.close.assert_called_once()

    @patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_cursor_closed_after_query(self, mock_sql_parser, mock_jdbc_jar_dict_class, mock_jaydebeapi):
        """Test that cursor is closed after query execution."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.SELECT

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [("id",)]
        mock_cursor.fetchmany.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_jaydebeapi.connect.return_value = mock_conn

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        data_source.export_data()

        mock_cursor.close.assert_called_once()

    @patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_uses_correct_file_name(self, mock_sql_parser, mock_jdbc_jar_dict_class, mock_jaydebeapi):
        """Test that export_data creates file with correct name."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.SELECT

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchmany.side_effect = [[(1, "Alice")], []]
        mock_conn.cursor.return_value = mock_cursor
        mock_jaydebeapi.connect.return_value = mock_conn

        custom_base_name = "custom_export"

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            base_file_name=custom_base_name,
            logger=self.mock_logger,
        )

        data_source.export_data()

        expected_file = os.path.join(self.temp_dir, f"{custom_base_name}_001.parquet")
        self.assertTrue(os.path.exists(expected_file))

    @patch("data_exchange_agent.data_sources.jdbc_data_source.jaydebeapi")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.JDBCJarDict")
    @patch("data_exchange_agent.data_sources.jdbc_data_source.get_read_only_sql_command_type")
    def test_export_data_logs_info_messages(self, mock_sql_parser, mock_jdbc_jar_dict_class, mock_jaydebeapi):
        """Test that export_data logs appropriate info messages."""
        mock_jdbc_jar_dict = Mock()
        mock_jdbc_jar_dict.get_jar_class_name.return_value = "org.postgresql.Driver"
        mock_jdbc_jar_dict.get_jar_path.return_value = "/path/to/postgresql.jar"
        mock_jdbc_jar_dict_class.return_value = mock_jdbc_jar_dict

        mock_sql_parser.return_value = SQLCommandType.SELECT

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [("id",)]
        mock_cursor.fetchmany.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_jaydebeapi.connect.return_value = mock_conn

        data_source = JDBCDataSource(
            source_authentication_info=self.auth_info,
            statement=self.statement,
            results_folder_path=self.temp_dir,
            logger=self.mock_logger,
        )

        data_source.export_data()

        # Check that info logging was called
        self.assertTrue(self.mock_logger.info.called)


if __name__ == "__main__":
    unittest.main()
