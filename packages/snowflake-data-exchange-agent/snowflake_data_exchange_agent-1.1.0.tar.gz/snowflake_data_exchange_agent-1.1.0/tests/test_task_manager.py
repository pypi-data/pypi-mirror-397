import os
import unittest

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from data_exchange_agent.data_sources.jdbc_data_source import JDBCDataSource
from data_exchange_agent.interfaces import TaskSourceAdapter
from data_exchange_agent.config.sections.connections.cloud_storages import SnowflakeConnectionNameConfig
from data_exchange_agent.config.sections.connections.jdbc.postgresql import PostgreSQLConnectionConfig
from data_exchange_agent.queues.sqlite_task_queue import SQLiteTaskQueue
from data_exchange_agent.tasks.manager import TaskManager
from data_exchange_agent.uploaders.azure_blob_uploader import AzureBlobUploader
from data_exchange_agent.utils.sf_logger import SFLogger


class TestTaskManager(unittest.TestCase):
    """
    Comprehensive test suite for the TaskManager class.

    This test class validates the TaskManager's core functionality, including:
    - Initialization with worker pools and task queues
    - Task fetching from API endpoints at configured intervals
    - Task execution using thread pool executors
    - Task status updates and result handling
    - Error handling and retry mechanisms
    - Graceful shutdown and cleanup procedures
    - Integration with SQLite task queues and API managers

    Tests use extensive mocking to isolate the TaskManager from external
    dependencies like databases, APIs, and file systems, ensuring reliable
    and fast test execution.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates a TaskManager instance with mocked TOML configuration
        to avoid file system dependencies. Sets up test database
        configuration and initializes the TaskManager with reduced
        worker count and fetch interval for faster test execution.
        """
        self.mock_logger = Mock(spec=SFLogger)
        # container = create_container()
        # container.sf_logger.override(self.mock_logger)
        # container.wire(
        #     modules=[
        #         "data_exchange_agent.utils.decorators",
        #         "data_exchange_agent.tasks.manager",
        #     ]
        # )
        self.mock_program_config = MagicMock()
        self.mock_program_config.__getitem__.side_effect = lambda key: {
            "application.workers": 8,
            "application.task_fetch_interval": 60,
            "application.debug_mode": True,
            "application.agent_id": "test_agent_id",
            "server.host": "127.0.0.1",
            "server.port": 8000,
            "connections.source": {
                "test_engine": PostgreSQLConnectionConfig(
                    host="localhost",
                    port=5432,
                    database="test",
                    username="test",
                    password="test",
                ),
            },
            "connections.target": {
                "test_bucket": {
                    "bucket": "test",
                    "region": "us-west-2",
                },
            },
        }[key]

        self.mock_task_source_adapter = Mock(spec=TaskSourceAdapter)

        # Directly pass the mock logger to bypass dependency injection
        self.task_manager = TaskManager(
            workers=2,
            tasks_fetch_interval=10,
            logger=self.mock_logger,
            program_config=self.mock_program_config,
            task_source_adapter=self.mock_task_source_adapter,
        )

    def test_task_manager_initialization(self):
        """Test TaskManager initialization with correct attributes."""
        self.assertEqual(self.task_manager.executor._max_workers, 2)
        self.assertEqual(self.task_manager.tasks_fetch_interval, 10)
        self.assertIsInstance(self.task_manager.task_queue, SQLiteTaskQueue)
        self.assertIsInstance(self.task_manager.task_source_adapter, TaskSourceAdapter)
        self.assertFalse(self.task_manager.stop_queue)
        self.assertFalse(self.task_manager.handling_tasks)
        self.assertFalse(self.task_manager.debug_mode)

    def test_task_manager_initialization_debug_mode_enabled(self):
        """Test TaskManager initialization with debug mode enabled via environment variable."""
        with patch.dict("os.environ", {"DEBUG_SINGLE_WORKER": "1"}):
            mock_logger = Mock(spec=SFLogger)
            task_manager = TaskManager(
                workers=8,  # Request 8 workers, but debug mode should override to 1
                tasks_fetch_interval=10,
                logger=mock_logger,
                program_config=self.mock_program_config,
                task_source_adapter=self.mock_task_source_adapter,
            )

            # Debug mode should be enabled
            self.assertTrue(task_manager.debug_mode)
            # Workers should be forced to 1 in debug mode
            self.assertEqual(task_manager.executor._max_workers, 1)
            # Should log debug mode message
            mock_logger.info.assert_called_with(
                "🐛 DEBUG MODE: Running in single-threaded synchronous mode for debugging"
            )

    def test_task_manager_initialization_debug_mode_disabled_by_default(self):
        """Test TaskManager debug mode is disabled when environment variable is not set."""
        with patch.dict("os.environ", {}, clear=True):
            # Ensure DEBUG_SINGLE_WORKER is not set
            if "DEBUG_SINGLE_WORKER" in os.environ:
                del os.environ["DEBUG_SINGLE_WORKER"]

            mock_logger = Mock(spec=SFLogger)
            task_manager = TaskManager(
                workers=4,
                tasks_fetch_interval=10,
                logger=mock_logger,
                program_config=self.mock_program_config,
                task_source_adapter=self.mock_task_source_adapter,
            )

            self.assertFalse(task_manager.debug_mode)
            self.assertEqual(task_manager.executor._max_workers, 4)

    def test_task_manager_initialization_debug_mode_disabled_with_wrong_value(self):
        """Test TaskManager debug mode is disabled when environment variable has wrong value."""
        with patch.dict("os.environ", {"DEBUG_SINGLE_WORKER": "0"}):
            mock_logger = Mock(spec=SFLogger)
            task_manager = TaskManager(
                workers=4,
                tasks_fetch_interval=10,
                logger=mock_logger,
                program_config=self.mock_program_config,
                task_source_adapter=self.mock_task_source_adapter,
            )

            self.assertFalse(task_manager.debug_mode)
            self.assertEqual(task_manager.executor._max_workers, 4)

    def test_stop_queue_property(self):
        """Test stop_queue property getter and setter."""
        self.assertFalse(self.task_manager.stop_queue)

        self.task_manager.stop_queue = True
        self.assertTrue(self.task_manager.stop_queue)

        self.task_manager.stop_queue = False
        self.assertFalse(self.task_manager.stop_queue)

    def test_add_task(self):
        """Test adding a task to the queue."""
        test_task = {"id": "123", "name": "test_task"}

        with patch.object(self.task_manager.task_queue, "add_task") as mock_add:
            self.task_manager.add_task(test_task)
            mock_add.assert_called_once_with(test_task)

    def test_get_tasks(self):
        """Test fetching tasks from API and adding to queue."""
        mock_tasks = [{"id": "1", "name": "task1"}, {"id": "2", "name": "task2"}]

        with (
            patch.object(self.task_manager.task_source_adapter, "get_tasks") as mock_get_tasks,
            patch.object(self.task_manager.task_queue, "add_task") as mock_add_task,
        ):
            mock_get_tasks.return_value = mock_tasks

            self.task_manager.get_tasks()

            mock_get_tasks.assert_called_once()
            self.assertEqual(mock_add_task.call_count, 2)
            mock_add_task.assert_any_call({"id": "1", "name": "task1"})
            mock_add_task.assert_any_call({"id": "2", "name": "task2"})

    def test_get_tasks_count(self):
        """Test getting task count from queue."""
        with patch.object(self.task_manager.task_queue, "get_queue_size") as mock_size:
            mock_size.return_value = 5

            result = self.task_manager.get_tasks_count()

            self.assertEqual(result, 5)
            mock_size.assert_called_once()

    def test_get_deque_id(self):
        """Test getting queue memory ID."""
        result = self.task_manager.get_deque_id()
        expected_id = id(self.task_manager.task_queue)

        self.assertEqual(result, expected_id)

    def test_get_completed_count(self):
        """Test getting completed task count from queue."""
        with patch.object(self.task_manager.task_queue, "get_completed_count") as mock_completed_count:
            mock_completed_count.return_value = 7

            result = self.task_manager.get_completed_count()

            self.assertEqual(result, 7)
            mock_completed_count.assert_called_once()

    def test_handle_tasks_first_time(self):
        """Test starting task handling for the first time."""
        with patch("threading.Thread") as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance

            self.task_manager.handle_tasks()

            self.assertTrue(self.task_manager.handling_tasks)
            mock_thread.assert_called_once_with(target=self.task_manager.task_loop, daemon=True)
            mock_thread_instance.start.assert_called_once()

    def test_handle_tasks_already_handling(self):
        """Test handle_tasks when already handling tasks."""
        self.task_manager.handling_tasks = True

        with (
            patch("threading.Thread") as mock_thread,
            patch("os.getpid") as mock_getpid,
        ):
            mock_getpid.return_value = 12345

            mock_logger = Mock()
            self.task_manager.logger = mock_logger
            self.task_manager.handle_tasks()

            mock_thread.assert_not_called()
            mock_logger.warning.assert_called_once_with(
                "TaskManager already handling tasks in PID 12345 with agent ID 'test_agent_id'."
            )

    def test_run_task(self):
        """Test submitting a task for execution via executor."""
        test_task = {"id": "123", "name": "test_task"}

        with patch.object(self.task_manager.executor, "submit") as mock_submit:
            self.task_manager.executor.submit(self.task_manager.process_task, test_task)

            mock_submit.assert_called_once_with(self.task_manager.process_task, test_task)

    def test_process_task_success(self):
        """Test successful task processing."""
        test_task = {
            "id": "123",
            "source_type": "jdbc_pyspark",
            "engine": "test_engine",
            "statement": "SELECT * FROM test_table",
            "upload_type": "s3",
            "upload_path": "/test/path",
        }

        mock_data_source_class = Mock()
        mock_data_source = Mock()
        mock_data_source_class.return_value = mock_data_source

        self.task_manager.source_connections_config = {
            "test_engine": PostgreSQLConnectionConfig(
                host="localhost",
                port=5432,
                database="test",
                username="test",
                password="test",
            ),
        }

        with (
            patch("data_exchange_agent.tasks.manager.DataSourceRegistry.create") as mock_data_source_registry_create,
            patch("data_exchange_agent.tasks.manager.build_actual_results_folder_path") as mock_build_path,
            patch("data_exchange_agent.tasks.manager.StorageProvider") as mock_storage_provider_class,
            patch.object(self.task_manager.task_source_adapter, "complete_task") as mock_complete_task_source_adapter,
            patch.object(self.task_manager.task_queue, "complete_task") as mock_complete_task,
        ):
            mock_data_source = Mock(spec=JDBCDataSource)
            mock_data_source_registry_create.return_value = mock_data_source

            mock_build_path.return_value = "/test/results/path"

            mock_storage_provider = Mock()
            mock_storage_provider_upload_files = Mock()
            mock_storage_provider_class.return_value = mock_storage_provider
            mock_storage_provider.upload_files = mock_storage_provider_upload_files

            self.task_manager.process_task(test_task)

            mock_data_source_registry_create.assert_called_once_with(
                "jdbc_pyspark",
                source_authentication_info=self.task_manager.source_connections_config["test_engine"],
                statement="SELECT * FROM test_table",
                results_folder_path="/test/results/path",
                base_file_name="task_123_result",
            )

            mock_data_source.export_data.assert_called_once()

            mock_storage_provider_upload_files.assert_called_once_with(
                "/test/results/path",
                "/test/path",
            )

            mock_complete_task_source_adapter.assert_called_once_with("123")
            mock_complete_task.assert_called_once_with("123")

    def test_task_loop_stop_condition(self):
        """Test task loop stops when stop_queue is True."""
        self.task_manager.stop_queue = True

        with (
            patch.object(self.task_manager, "get_tasks") as mock_get_tasks,
            patch("time.sleep"),
        ):
            self.task_manager.task_loop()

            self.assertFalse(self.task_manager.handling_tasks)
            self.assertFalse(self.task_manager.stop_queue)

            mock_get_tasks.assert_not_called()

    def test_task_loop_processes_tasks(self):
        """Test task loop processes available tasks."""
        test_task = {"id": "123", "name": "test_task"}

        with (
            patch.object(self.task_manager, "get_tasks"),
            patch.object(self.task_manager.task_queue, "get_task") as mock_get_task,
            patch.object(self.task_manager.executor, "submit") as mock_submit,
            patch("time.sleep") as mock_sleep,
        ):
            mock_get_task.side_effect = [test_task, None]

            def stop_after_first_iteration(*args):
                self.task_manager.stop_queue = True

            mock_sleep.side_effect = stop_after_first_iteration

            self.task_manager.task_loop()

            mock_submit.assert_called_once_with(self.task_manager.process_task, test_task)

    def test_task_loop_processes_tasks_synchronously_in_debug_mode(self):
        """Test task loop processes tasks synchronously when debug mode is enabled."""
        test_task = {"id": "123", "name": "test_task"}

        # Enable debug mode
        self.task_manager.debug_mode = True

        with (
            patch.object(self.task_manager, "get_tasks"),
            patch.object(self.task_manager.task_queue, "get_task") as mock_get_task,
            patch.object(self.task_manager.executor, "submit") as mock_submit,
            patch.object(self.task_manager, "process_task") as mock_process_task,
            patch("time.sleep") as mock_sleep,
        ):
            mock_get_task.side_effect = [test_task, None]

            def stop_after_first_iteration(*args):
                self.task_manager.stop_queue = True

            mock_sleep.side_effect = stop_after_first_iteration

            mock_logger = Mock()
            self.task_manager.logger = mock_logger

            self.task_manager.task_loop()

            # In debug mode, executor.submit should NOT be called
            mock_submit.assert_not_called()
            # Instead, process_task should be called directly (synchronously)
            mock_process_task.assert_called_once_with(test_task)
            # Debug mode log message should be shown
            mock_logger.info.assert_called_with("🐛 DEBUG MODE: Processing task synchronously")

    def test_task_loop_uses_thread_pool_when_debug_mode_disabled(self):
        """Test task loop uses thread pool executor when debug mode is disabled."""
        test_task = {"id": "456", "name": "test_task"}

        # Ensure debug mode is disabled
        self.task_manager.debug_mode = False

        with (
            patch.object(self.task_manager, "get_tasks"),
            patch.object(self.task_manager.task_queue, "get_task") as mock_get_task,
            patch.object(self.task_manager.executor, "submit") as mock_submit,
            patch.object(self.task_manager, "process_task") as mock_process_task,
            patch("time.sleep") as mock_sleep,
        ):
            mock_get_task.side_effect = [test_task, None]

            def stop_after_first_iteration(*args):
                self.task_manager.stop_queue = True

            mock_sleep.side_effect = stop_after_first_iteration

            self.task_manager.task_loop()

            # In normal mode, executor.submit should be called
            mock_submit.assert_called_once_with(self.task_manager.process_task, test_task)
            # process_task should NOT be called directly
            mock_process_task.assert_not_called()

    def test_task_loop_exception_handling(self):
        """Test task loop handles exceptions gracefully."""
        with (
            patch.object(self.task_manager, "get_tasks") as mock_get_tasks,
            patch("time.sleep") as mock_sleep,
        ):
            api_exception_error = Exception("API error")
            mock_get_tasks.side_effect = api_exception_error

            def stop_after_first_iteration(*args):
                self.task_manager.stop_queue = True

            mock_sleep.side_effect = stop_after_first_iteration

            mock_logger = Mock()
            self.task_manager.logger = mock_logger

            self.task_manager.task_loop()

            mock_logger.error.assert_called_once_with("Error in task_loop: API error", exception=api_exception_error)

    def test_process_task_error_handling(self):
        """Test process_task handles exceptions and logs errors properly."""
        task = {
            "id": "123",
            "source_type": "jdbc",
            "engine": "test_engine",
            "statement": "SELECT * FROM test",
            "destination_path": "/test/path",
            "upload_method": "snowflake-stage",
        }

        # Mock the data source to raise an exception
        with patch("data_exchange_agent.tasks.manager.DataSourceRegistry.create") as mock_data_source_registry_create:
            mock_data_source_registry_create.side_effect = Exception("Data source registry create error")

            # Mock API manager
            mock_task_source_adapter = Mock()
            self.task_manager.task_source_adapter = mock_task_source_adapter

            # Execute process_task
            self.task_manager.process_task(task)

            # Verify error was logged
            error_message = "Error processing the task '123'. Failed creating the 'jdbc' data source."
            self.mock_logger.error.assert_called_with(error_message, exception=unittest.mock.ANY)

            # Verify task was marked as failed
            mock_task_source_adapter.fail_task.assert_called_once_with("123", error_message)

    @patch("data_exchange_agent.tasks.manager.DataSourceRegistry.create")
    @patch("data_exchange_agent.tasks.manager.SQLiteTaskQueue.complete_task")
    @patch("data_exchange_agent.providers.storageProvider.delete_folder_file")
    @patch("data_exchange_agent.providers.storageProvider.AzureBlobUploader")
    @patch("os.listdir")
    @patch("data_exchange_agent.tasks.manager.build_actual_results_folder_path")
    def test_upload_to_azure_blob_success(
        self,
        mock_build_actual_results_folder_path,
        mock_os_listdir,
        mock_azure_blob_uploader,
        mock_delete_folder_file,
        mock_complete_task,
        mock_data_source_registry_create,
    ):
        """Test successful upload to Azure Blob Storage."""
        mock_data_source_registry_create.return_value = Mock(spec=JDBCDataSource)
        mock_build_actual_results_folder_path.return_value = str(Path("/test/results/path"))
        mock_os_listdir.side_effect = lambda x: ["test.parquet"] if x == str(Path("/test/results/path")) else []
        mock_azure_blob_uploader.return_value = MagicMock(spec=AzureBlobUploader)
        mock_azure_blob_uploader.return_value.__enter__.return_value = mock_azure_blob_uploader
        mock_azure_blob_uploader.return_value.__exit__.return_value = False
        mock_azure_blob_uploader.upload_files = Mock()

        # Mock cloud storage configuration
        self.task_manager.target_connections_config = {
            # TODO: replace with actual AZURE blob connection config
            "blob": SnowflakeConnectionNameConfig(
                connection_name="test",
            ),
        }

        task = {
            "id": "123",
            "source_type": "jdbc_pyspark",
            "engine": "test_engine",
            "statement": "SELECT * FROM test",
            "upload_type": "blob",
            "upload_path": "/test/path",
        }

        self.task_manager.process_task(task)
        # Verify configuration was set
        self.assertEqual(mock_delete_folder_file.call_count, 1)
        self.assertEqual(mock_azure_blob_uploader.call_count, 1)

        # Verify upload_files was called
        mock_azure_blob_uploader.upload_files.assert_called_once_with(
            str(Path("/test/results/path/test.parquet")), destination_path="/test/path"
        )

        self.mock_task_source_adapter.complete_task.assert_called_once_with("123")

        mock_complete_task.assert_called_once_with("123")


if __name__ == "__main__":
    unittest.main()
