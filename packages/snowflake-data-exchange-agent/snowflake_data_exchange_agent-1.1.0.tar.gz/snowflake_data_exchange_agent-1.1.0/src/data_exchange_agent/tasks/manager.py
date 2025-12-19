"""
Task management and execution system.

This module provides the TaskManager class which orchestrates task execution
across multiple worker threads, handles task lifecycle management, API
communication, and integrates with various data sources and uploaders.
"""

import json
import os
import threading
import time

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from dependency_injector.wiring import Provide, inject
from py4j.protocol import Py4JJavaError

from data_exchange_agent.config.manager import ConfigManager
from data_exchange_agent.config.sections.connections.cloud_storages.base import BaseCloudStorageConnectionConfig
from data_exchange_agent.config.sections.connections.jdbc.base import BaseJDBCConnectionConfig
from data_exchange_agent.constants import config_keys, container_keys, task_keys
from data_exchange_agent.constants.config_defaults import (
    DEFAULT__APPLICATION__TASK_FETCH_INTERVAL,
    DEFAULT__APPLICATION__WORKERS,
)
from data_exchange_agent.constants.paths import (
    build_actual_results_folder_path,
)
from data_exchange_agent.data_sources import BaseDataSource, DataSourceRegistry
from data_exchange_agent.interfaces.task_queue import TaskQueueInterface
from data_exchange_agent.interfaces.task_source_adapter import TaskSourceAdapter
from data_exchange_agent.providers.storageProvider import StorageProvider
from data_exchange_agent.queues.sqlite_task_queue import SQLiteTaskQueue
from data_exchange_agent.utils.decorators import log_error
from data_exchange_agent.utils.sf_logger import SFLogger
from snowflake.connector import errors as snowflake_errors


class TaskManager:
    """
    Manages asynchronous task processing using a thread pool and task queue.

    This class handles fetching, queueing and processing of data extraction tasks.
    It maintains a thread pool for parallel task execution and uses a thread-safe
    task queue.

    Attributes:
        debug_mode (bool): Whether to run in debug mode
        executor (ThreadPoolExecutor): Thread pool for executing tasks
        task_queue (TaskQueueInterface): Thread-safe queue of tasks to process
        stop_queue (bool): Flag to stop task processing
        tasks_fetch_interval (int): Seconds between task fetch attempts
        handling_tasks (bool): Whether tasks are currently being handled
        agent_id (str): Agent ID
        source_connections_config (dict[str, BaseJDBCConnectionConfig]): Database connection configurations
        target_connections_config (dict[str, BaseCloudStorageConnectionConfig]): Cloud storage connection configurations
        sources (dict[str, DataSourceInterface]): Data source classes

    Args:
        workers (int, optional): Number of worker threads. Defaults to DEFAULT_WORKERS_COUNT.
        tasks_fetch_interval (int, optional): Task fetch interval in seconds. Defaults to DEFAULT_TASKS_FETCH_INTERVAL.

    """

    @property
    def stop_queue(self) -> bool:
        """
        Get the stop queue flag.

        Returns:
            bool: True if queue processing should stop, False otherwise

        """
        return self._stop_queue

    @stop_queue.setter
    def stop_queue(self, value: bool) -> None:
        """
        Set the stop queue flag.

        Args:
            value (bool): True to stop queue processing, False to continue

        """
        self._stop_queue = value

    @log_error
    @inject
    def __init__(
        self,
        workers: int = DEFAULT__APPLICATION__WORKERS,
        tasks_fetch_interval: int = DEFAULT__APPLICATION__TASK_FETCH_INTERVAL,
        logger: SFLogger = Provide[container_keys.SF_LOGGER],
        program_config: ConfigManager = Provide[container_keys.PROGRAM_CONFIG],
        task_source_adapter: TaskSourceAdapter = Provide[container_keys.TASK_SOURCE_ADAPTER],
    ) -> None:
        """
        Initialize the TaskManager with specified configuration.

        Sets up the task execution environment including thread pool executor,
        task queue, task source adapter, and loads configuration from TOML file.
        Initializes all necessary components for managing and processing tasks.

        Args:
            workers (int): Number of worker threads for concurrent task execution.
                         Defaults to DEFAULT_WORKERS_COUNT.
            tasks_fetch_interval (int): Interval in seconds between API task fetches.
                                      Defaults to DEFAULT_TASKS_FETCH_INTERVAL seconds.
            logger (SFLogger): Logger instance for logging messages.
                             Defaults to injected sf_logger.
            program_config (ConfigManager): Program configuration
            task_source_adapter (TaskSourceAdapter): Task source adapter instance.
                             Defaults to injected task_source_adapter.

        Raises:
            Exception: If the configuration TOML file cannot be loaded.
            custom_exceptions.ConfigurationError: If something was wrong with the configuration TOML file.

        """
        self.logger = logger
        # Check if debug mode is enabled (for better debugging with breakpoints)
        self.debug_mode = os.getenv("DEBUG_SINGLE_WORKER") == "1"
        if self.debug_mode:
            self.logger.info("🐛 DEBUG MODE: Running in single-threaded synchronous mode for debugging")
            workers = 1
        self.executor = ThreadPoolExecutor(max_workers=workers)
        self.task_queue: TaskQueueInterface = SQLiteTaskQueue()
        self.stop_queue = False
        self.task_source_adapter = task_source_adapter
        self.tasks_fetch_interval = tasks_fetch_interval
        self.handling_tasks = False
        self.agent_id = program_config[config_keys.APPLICATION__AGENT_ID]

        self.source_connections_config: dict[str, BaseJDBCConnectionConfig] = program_config[
            config_keys.CONNECTIONS__SOURCE
        ]
        self.target_connections_config: dict[str, BaseCloudStorageConnectionConfig] = program_config[
            config_keys.CONNECTIONS__TARGET
        ]

    @log_error
    def add_task(self, task: dict[str, Any]) -> None:
        """
        Add a single task to the task queue.

        Args:
            task (dict[str, any]): Task configuration dictionary

        """
        self.task_queue.add_task(task)

    @log_error
    def get_tasks(self) -> None:
        """Fetch tasks from API and add them to the task queue."""
        tasks = self.task_source_adapter.get_tasks()
        for task in tasks:
            self.task_queue.add_task(task)

    @log_error
    def get_tasks_count(self) -> int:
        """
        Get current number of tasks in queue.

        Returns:
            int: Number of tasks in queue

        """
        return self.task_queue.get_queue_size()

    @log_error
    def get_deque_id(self) -> int:
        """
        Get memory ID of task queue.

        Returns:
            int: Memory ID of task queue object

        """
        return id(self.task_queue)

    @log_error
    def get_completed_count(self) -> int:
        """
        Get the number of completed tasks.

        Returns:
            Number of completed tasks

        """
        return self.task_queue.get_completed_count()

    @log_error
    def handle_tasks(self) -> None:
        """
        Start task handling in a background thread.

        Creates a daemon thread to process tasks if not already running.
        """
        if self.handling_tasks:
            self.logger.warning(
                f"TaskManager already handling tasks in PID {os.getpid()} with agent ID '{self.agent_id}'."
            )
            return
        self.handling_tasks = True
        self.logger.info(f"Starting handling tasks in PID {os.getpid()} with agent ID '{self.agent_id}'.")
        task_thread = threading.Thread(target=self.task_loop, daemon=True)
        task_thread.start()

    def task_loop(self) -> None:
        """
        Process tasks continuously in a loop.

        Continuously fetches and processes tasks from the queue until stopped.
        Handles task retrieval, execution and error handling.
        """
        while True:
            try:
                if self.stop_queue:
                    self.handling_tasks = False
                    self.stop_queue = False
                    break

                self.get_tasks()

                while True:
                    task = self.task_queue.get_task()

                    if task:
                        if self.debug_mode:
                            # In debug mode, run synchronously so breakpoints work properly
                            self.logger.info("🐛 DEBUG MODE: Processing task synchronously")
                            self.process_task(task)
                        else:
                            # Normal mode: submit to thread pool
                            self.executor.submit(self.process_task, task)
                        time.sleep(0.5)
                    else:
                        break

            except Exception as e:
                self.logger.error(f"Error in task_loop: {str(e)}", exception=e)
            finally:
                time.sleep(self.tasks_fetch_interval)

    def process_task(self, task: dict[str, any]) -> None:
        """
        Process a single data extraction task.

        Creates appropriate data source, extracts data and saves to parquet.
        Updates task status on completion.

        Args:
            task (dict[str, any]): Task configuration dictionary

        """
        task_id = task.get(task_keys.ID)
        formatted_task = json.dumps(task, indent=4)
        self.logger.info(f"🚀 Processing task '{task_id}': {formatted_task}")

        # Get the engine configuration
        engine = task.get(task_keys.ENGINE)
        if engine in self.source_connections_config:
            engine_config: BaseJDBCConnectionConfig = self.source_connections_config[engine]
        else:
            message = f"Engine {engine} not found in source connections configuration."
            self._handle_error(task, message)
            return

        # Create the data source
        data_source_name = None
        try:
            data_source_name = task.get(task_keys.SOURCE_TYPE)
            statement = task.get(task_keys.STATEMENT)
            results_folder_path = build_actual_results_folder_path(task_id)
            base_file_name = f"task_{task_id}_result"
            data_source: BaseDataSource = DataSourceRegistry.create(
                data_source_name,
                source_authentication_info=engine_config,
                statement=statement,
                results_folder_path=results_folder_path,
                base_file_name=base_file_name,
            )
        except Exception as e:
            message = f"Failed creating the '{data_source_name}' data source."
            self._handle_error(task, message, e)
            return

        # Export the data from the data source
        try:
            if not data_source.export_data():
                raise Exception("Failed exporting data from the data source.")
        except Exception as e:
            message = (
                f"Failed exporting data from the '{task[task_keys.ENGINE]}' engine "
                f"using the '{data_source_name}' data source."
            )
            self._handle_jdbc_error(task, message, e)
            return

        # Upload the data
        try:
            storage_provider = StorageProvider(task[task_keys.UPLOAD_TYPE], self.target_connections_config)
            storage_provider.upload_files(results_folder_path, task[task_keys.UPLOAD_PATH])
        except Exception as e:
            message = f"Failed uploading the results to the '{task[task_keys.UPLOAD_TYPE]}' cloud storage."
            self._handle_cloud_storage_error(task, message, e)
            return

        # Handle success
        self._handle_success(task)

    def _handle_success(self, task: dict[str, any]) -> None:
        task_id = task[task_keys.ID]
        try:
            self.task_source_adapter.complete_task(task_id)
            self.task_queue.complete_task(task_id)
        except Exception as e:
            self._handle_error(task, f"Failed handling completion of task '{task_id}'.", e)

    def _handle_error(self, task: dict[str, any], message: str, exception: Exception | None = None) -> None:
        task_id = task[task_keys.ID]
        message = f"Error processing the task '{task_id}'. {message}"
        self.logger.error(message, exception=exception)
        try:
            self.task_source_adapter.fail_task(task_id, message)
            self.task_queue.fail_task(task_id, message)
        except Exception as e:
            self.logger.error(f"Failed handling failure of task '{task_id}'.", exception=e)

    def _handle_jdbc_error(self, task: dict[str, any], message: str, exception: Exception | None = None) -> None:
        if isinstance(exception, Py4JJavaError):
            exception_message = str(exception)
            if (
                "com.microsoft.sqlserver.jdbc.SQLServerException" in exception_message  # SQL Server specific exception
                and "Connection refused" in exception_message  # Connection refused exception
            ):
                message += (
                    "\nVerify the connection properties. "
                    "Make sure that an instance of SQL Server is running on the host "
                    "and accepting TCP/IP connections at the port. "
                    "Make sure that TCP connections to the port are not blocked by a firewall."
                )
                self._handle_error(task, message)
                return

        message += "\nPlease check the database connection and the query."
        self._handle_error(task, message, exception)

    def _handle_cloud_storage_error(
        self, task: dict[str, any], message: str, exception: Exception | None = None
    ) -> None:
        if isinstance(exception, snowflake_errors.DatabaseError | snowflake_errors.HttpError):
            message += f" {str(exception)}"
            self._handle_error(task, message)
        else:
            self._handle_error(task, message, exception)
