"""
Tests for the SnowflakeStoredProcedureTaskSourceAdapter class.

This module tests the SnowflakeStoredProcedureTaskSourceAdapter to ensure it properly
handles task retrieval, completion, and failure operations with Snowflake stored procedures.
"""

import json
import unittest

from unittest.mock import MagicMock, Mock, patch

from data_exchange_agent import custom_exceptions
from data_exchange_agent.task_sources.snowflake_stored_procedure import (
    SnowflakeStoredProcedureTaskSourceAdapter,
)


class TestSnowflakeStoredProcedureTaskSourceAdapter(unittest.TestCase):
    """
    Comprehensive test suite for the SnowflakeStoredProcedureTaskSourceAdapter class.

    This test class validates the adapter's core functionality, including:
    - Initialization with proper configuration
    - Task retrieval from Snowflake stored procedures
    - Task completion status updates
    - Task failure status updates
    - Error handling for various failure scenarios
    - Proper interaction with SnowflakeDataSource

    Tests use extensive mocking to isolate the adapter from external
    dependencies like Snowflake connections, ensuring reliable and fast test execution.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates a mock configuration and SnowflakeStoredProcedureTaskSourceAdapter instance
        to avoid external dependencies during testing.
        """
        # Create mock configuration
        self.mock_task_source = Mock()
        self.mock_task_source.connection_name = "test_snowflake_connection"

        self.mock_program_config = MagicMock()
        self.mock_program_config.__getitem__.side_effect = lambda key: {
            "task_source": self.mock_task_source,
            "application.agent_id": "test_agent_123",
        }[key]

    def test_initialization_success(self):
        """Test successful initialization with valid configuration."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource:
            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)

            self.assertEqual(adapter.connection_name, "test_snowflake_connection")
            self.assertEqual(adapter.agent_id, "test_agent_123")
            mock_sf_datasource.assert_called_once_with(connection_name="test_snowflake_connection")

    def test_initialization_missing_connection_name(self):
        """Test initialization fails when connection_name is missing."""
        mock_program_config = MagicMock()
        mock_program_config.__getitem__.side_effect = KeyError("task_source")

        with patch("data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"):
            with self.assertRaises(custom_exceptions.ConfigurationError) as context:
                SnowflakeStoredProcedureTaskSourceAdapter(program_config=mock_program_config)

            self.assertIn(
                "Snowflake stored procedure task source configuration is missing or incomplete",
                str(context.exception),
            )
            self.assertIn("connection_name", str(context.exception))

    def test_initialization_missing_connection_name_attribute(self):
        """Test initialization fails when connection_name attribute is missing."""
        mock_task_source = Mock()
        del mock_task_source.connection_name

        mock_program_config = MagicMock()
        mock_program_config.__getitem__.side_effect = lambda key: {
            "task_source": mock_task_source,
            "application.agent_id": "test_agent_123",
        }[key]

        with patch("data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"):
            with self.assertRaises(custom_exceptions.ConfigurationError) as context:
                SnowflakeStoredProcedureTaskSourceAdapter(program_config=mock_program_config)

            self.assertIn(
                "Snowflake stored procedure task source configuration is missing or incomplete",
                str(context.exception),
            )

    def test_initialization_missing_agent_id(self):
        """Test initialization fails when agent_id is missing."""
        mock_program_config = MagicMock()

        def mock_getitem(key):
            if key == "task_source":
                return self.mock_task_source
            raise KeyError(key)

        mock_program_config.__getitem__.side_effect = mock_getitem

        with patch("data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"):
            with self.assertRaises(custom_exceptions.ConfigurationError) as context:
                SnowflakeStoredProcedureTaskSourceAdapter(program_config=mock_program_config)

            self.assertIn("Agent ID is missing or incomplete", str(context.exception))

    def test_get_tasks_success(self):
        """Test successful task retrieval from Snowflake stored procedure."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            # Set up mock data source
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance

            # Mock the context manager behavior
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Mock raw task data returned from Snowflake
            raw_task_payload = {
                "source_type": "postgresql",
                "database": "test_db",
                "schema": "public",
                "statement_location_id": "SELECT * FROM users",
                "target_type": "s3",
                "target_id": "s3://bucket/path/data",
            }

            raw_tasks = [
                {
                    "ID": "task_001",
                    "PAYLOAD": json.dumps(raw_task_payload),
                }
            ]

            mock_context.execute_statement.return_value = raw_tasks

            # Create adapter and call get_tasks
            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)
            result = adapter.get_tasks()

            # Verify the stored procedure call
            call_args = mock_context.execute_statement.call_args[0][0]
            self.assertIn("CALL SNOWCONVERT_AI.DATA_MIGRATION.PULL_TASKS", call_args)
            self.assertIn("test_agent_123", call_args)
            self.assertIn("data-exchange-agent", call_args)

            # Verify the result
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["id"], "task_001")
            self.assertEqual(result[0]["engine"], "postgresql")
            self.assertEqual(result[0]["database"], "test_db")
            self.assertEqual(result[0]["schema"], "public")
            self.assertEqual(result[0]["statement"], "SELECT * FROM users")
            self.assertEqual(result[0]["source_type"], "jdbc")
            self.assertEqual(result[0]["upload_type"], "s3")
            self.assertEqual(result[0]["upload_path"], "s3://bucket/path/data")

    def test_get_tasks_multiple_tasks(self):
        """Test retrieval of multiple tasks from Snowflake stored procedure."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Mock multiple tasks
            raw_tasks = [
                {
                    "ID": "task_001",
                    "PAYLOAD": json.dumps(
                        {
                            "source_type": "postgresql",
                            "database": "db1",
                            "schema": "schema1",
                            "statement_location_id": "SELECT 1",
                            "target_type": "s3",
                            "target_id": "s3://bucket1/path1",
                        }
                    ),
                },
                {
                    "ID": "task_002",
                    "PAYLOAD": json.dumps(
                        {
                            "source_type": "mysql",
                            "database": "db2",
                            "schema": "schema2",
                            "statement_location_id": "SELECT 2",
                            "target_type": "azure",
                            "target_id": "azure://container/path2",
                        }
                    ),
                },
            ]

            mock_context.execute_statement.return_value = raw_tasks

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)
            result = adapter.get_tasks()

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["id"], "task_001")
            self.assertEqual(result[0]["engine"], "postgresql")
            self.assertEqual(result[1]["id"], "task_002")
            self.assertEqual(result[1]["engine"], "mysql")

    def test_get_tasks_empty_list(self):
        """Test get_tasks when no tasks are available."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Return empty list
            mock_context.execute_statement.return_value = []

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)
            result = adapter.get_tasks()

            self.assertEqual(result, [])
            self.assertIsInstance(result, list)

    def test_get_tasks_execution_failure(self):
        """Test get_tasks when Snowflake execution fails."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Simulate execution failure
            mock_context.execute_statement.side_effect = Exception("Snowflake connection error")

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)

            with self.assertRaises(Exception) as context:
                adapter.get_tasks()

            self.assertIn("Failed to pull tasks executing statement", str(context.exception))
            self.assertIn("PULL_TASKS", str(context.exception))

    def test_get_tasks_json_parse_error(self):
        """Test get_tasks when JSON payload parsing fails."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Return invalid JSON
            raw_tasks = [{"ID": "task_001", "PAYLOAD": "invalid json{"}]
            mock_context.execute_statement.return_value = raw_tasks

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)

            with self.assertRaises(Exception) as context:
                adapter.get_tasks()

            self.assertIn("Failed to pull tasks executing statement", str(context.exception))

    def test_complete_task_success(self):
        """Test successful task completion."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Mock successful completion response
            mock_context.execute_statement.return_value = [{"COMPLETE_TASK": True}]

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)
            adapter.complete_task("task_123")

            # Verify the stored procedure call
            call_args = mock_context.execute_statement.call_args[0][0]
            self.assertIn("CALL SNOWCONVERT_AI.DATA_MIGRATION.COMPLETE_TASK", call_args)
            self.assertIn("test_agent_123", call_args)
            self.assertIn("task_123", call_args)

    def test_complete_task_returns_false(self):
        """Test complete_task when stored procedure returns False."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Mock failed completion response
            mock_context.execute_statement.return_value = [{"COMPLETE_TASK": False}]

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)

            with self.assertRaises(Exception) as context:
                adapter.complete_task("task_123")

            self.assertIn("Failed to mark task 'task_123' as completed", str(context.exception))

    def test_complete_task_returns_none(self):
        """Test complete_task when stored procedure returns None."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Mock None response (no results)
            mock_context.execute_statement.return_value = []

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)

            with self.assertRaises(Exception) as context:
                adapter.complete_task("task_123")

            self.assertIn("Failed to mark task 'task_123' as completed", str(context.exception))

    def test_complete_task_execution_failure(self):
        """Test complete_task when Snowflake execution fails."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Simulate execution failure
            mock_context.execute_statement.side_effect = Exception("Database error")

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)

            with self.assertRaises(Exception) as context:
                adapter.complete_task("task_123")

            self.assertIn("Failed to mark task 'task_123' as completed", str(context.exception))
            self.assertIn("COMPLETE_TASK", str(context.exception))

    def test_fail_task_success_without_error_message(self):
        """Test successful task failure marking without error message."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Mock successful failure response
            mock_context.execute_statement.return_value = [{"FAIL_TASK": True}]

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)
            adapter.fail_task("task_456")

            # Verify the stored procedure call
            call_args = mock_context.execute_statement.call_args[0][0]
            self.assertIn("CALL SNOWCONVERT_AI.DATA_MIGRATION.FAIL_TASK", call_args)
            self.assertIn("test_agent_123", call_args)
            self.assertIn("task_456", call_args)
            # Should not contain error message parameter
            self.assertEqual(call_args.count(","), 2)  # Only 3 parameters

    def test_fail_task_success_with_error_message(self):
        """Test successful task failure marking with error message."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Mock successful failure response
            mock_context.execute_statement.return_value = [{"FAIL_TASK": True}]

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)
            adapter.fail_task("task_456", "Connection timeout error")

            # Verify the stored procedure call
            call_args = mock_context.execute_statement.call_args[0][0]
            self.assertIn("CALL SNOWCONVERT_AI.DATA_MIGRATION.FAIL_TASK", call_args)
            self.assertIn("Connection timeout error", call_args)
            self.assertEqual(call_args.count(","), 2)  # 2 parameters

    def test_fail_task_with_error_message_containing_quotes(self):
        """Test fail_task with error message containing single quotes."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Mock successful failure response
            mock_context.execute_statement.return_value = [{"FAIL_TASK": True}]

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)
            adapter.fail_task("task_456", "Error: Can't connect to 'database'")

            # Verify the stored procedure call with escaped quotes
            call_args = mock_context.execute_statement.call_args[0][0]
            self.assertIn("Error: Can''t connect to ''database''", call_args)

    def test_fail_task_returns_false(self):
        """Test fail_task when stored procedure returns False."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Mock failed response
            mock_context.execute_statement.return_value = [{"FAIL_TASK": False}]

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)

            with self.assertRaises(Exception) as context:
                adapter.fail_task("task_456", "Test error")

            self.assertIn("Failed to mark task 'task_456' as failed", str(context.exception))

    def test_fail_task_returns_none(self):
        """Test fail_task when stored procedure returns None."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Mock None response
            mock_context.execute_statement.return_value = []

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)

            with self.assertRaises(Exception) as context:
                adapter.fail_task("task_456")

            self.assertIn("Failed to mark task 'task_456' as failed", str(context.exception))

    def test_fail_task_execution_failure(self):
        """Test fail_task when Snowflake execution fails."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            # Simulate execution failure
            mock_context.execute_statement.side_effect = Exception("Network error")

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)

            with self.assertRaises(Exception) as context:
                adapter.fail_task("task_456", "Original error")

            self.assertIn("Failed to mark task 'task_456' as failed", str(context.exception))
            self.assertIn("FAIL_TASK", str(context.exception))

    def test_adapter_constants(self):
        """Test that adapter class constants are properly defined."""
        self.assertEqual(SnowflakeStoredProcedureTaskSourceAdapter.SCHEMA, "SNOWCONVERT_AI.DATA_MIGRATION")
        self.assertEqual(SnowflakeStoredProcedureTaskSourceAdapter.WORKFLOW_ID, "data-migration-1")
        self.assertEqual(SnowflakeStoredProcedureTaskSourceAdapter.AGENT_TYPE, "data-exchange-agent")
        self.assertEqual(SnowflakeStoredProcedureTaskSourceAdapter.MAX_TASKS_PER_FETCH, 1)
        self.assertEqual(SnowflakeStoredProcedureTaskSourceAdapter.PULL_TASKS_SP_NAME, "PULL_TASKS")
        self.assertEqual(SnowflakeStoredProcedureTaskSourceAdapter.COMPLETE_TASK_SP_NAME, "COMPLETE_TASK")
        self.assertEqual(SnowflakeStoredProcedureTaskSourceAdapter.FAIL_TASK_SP_NAME, "FAIL_TASK")

    def test_adapter_inherits_from_task_source_adapter(self):
        """Test that SnowflakeStoredProcedureTaskSourceAdapter inherits from TaskSourceAdapter."""
        with patch("data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"):
            from data_exchange_agent.interfaces.task_source_adapter import TaskSourceAdapter

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)
            self.assertIsInstance(adapter, TaskSourceAdapter)

    def test_context_manager_properly_used(self):
        """Test that SnowflakeDataSource context manager is properly used."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context
            mock_context.execute_statement.return_value = []

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)
            adapter.get_tasks()

            # Verify context manager was used
            mock_sf_instance.__enter__.assert_called_once()
            mock_sf_instance.__exit__.assert_called_once()

    def test_get_tasks_with_complex_statement(self):
        """Test get_tasks with complex SQL statement in payload."""
        with patch(
            "data_exchange_agent.task_sources.snowflake_stored_procedure.SnowflakeDataSource"
        ) as mock_sf_datasource_class:
            mock_sf_instance = MagicMock()
            mock_sf_datasource_class.return_value = mock_sf_instance
            mock_context = MagicMock()
            mock_sf_instance.__enter__.return_value = mock_context

            complex_statement = """
                WITH cte AS (
                    SELECT * FROM table1
                    WHERE condition = 'test'
                )
                SELECT a.*, b.* FROM cte a
                JOIN table2 b ON a.id = b.id
            """

            raw_task_payload = {
                "source_type": "postgresql",
                "database": "test_db",
                "schema": "public",
                "statement_location_id": complex_statement,
                "target_type": "s3",
                "target_id": "s3://bucket/path",
            }

            raw_tasks = [{"ID": "task_complex", "PAYLOAD": json.dumps(raw_task_payload)}]
            mock_context.execute_statement.return_value = raw_tasks

            adapter = SnowflakeStoredProcedureTaskSourceAdapter(program_config=self.mock_program_config)
            result = adapter.get_tasks()

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["statement"], complex_statement)


if __name__ == "__main__":
    unittest.main()
