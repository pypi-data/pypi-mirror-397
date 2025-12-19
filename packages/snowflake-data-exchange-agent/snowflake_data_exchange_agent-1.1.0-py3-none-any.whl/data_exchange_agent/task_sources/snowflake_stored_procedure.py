"""
Snowflake stored procedure task source adapter.

This module provides the SnowflakeStoredProcedureTaskSourceAdapter class for managing
communication with Snowflake stored procedures, including task retrieval and status updates.
"""

import json

from dependency_injector.wiring import Provide, inject

from data_exchange_agent import custom_exceptions
from data_exchange_agent.config import ConfigManager
from data_exchange_agent.constants import config_keys, container_keys
from data_exchange_agent.data_sources.sf_connection import SnowflakeDataSource
from data_exchange_agent.interfaces.task_source_adapter import TaskSourceAdapter
from data_exchange_agent.tasks.task import Task


class SnowflakeStoredProcedureTaskSourceAdapter(TaskSourceAdapter):
    """
    Manages Snowflake stored procedure interactions for the Data Exchange Agent.

    This class handles communication with the Snowflake stored procedure, including:
    - Loading Snowflake stored procedure configuration
    - Retrieving tasks from the Snowflake stored procedure
    - Updating task status and details

    The Snowflake stored procedure configuration is loaded from a TOML configuration file
    and used to configure the Snowflake stored procedure.
    """

    SCHEMA = "SNOWCONVERT_AI.DATA_MIGRATION"
    WORKFLOW_ID = "data-migration-1"
    AGENT_TYPE = "data-exchange-agent"
    MAX_TASKS_PER_FETCH = 1
    PULL_TASKS_SP_NAME = "PULL_TASKS"
    COMPLETE_TASK_SP_NAME = "COMPLETE_TASK"
    FAIL_TASK_SP_NAME = "FAIL_TASK"
    COMPLETED_TASK_STATUS_KEY = COMPLETE_TASK_SP_NAME  # The SP returns a scalar value, so key's result is the SP name
    FAILED_TASK_STATUS_KEY = FAIL_TASK_SP_NAME  # The SP returns a scalar value, so key's result is the SP name

    @inject
    def __init__(self, program_config: ConfigManager = Provide[container_keys.PROGRAM_CONFIG]) -> None:
        """
        Initialize the SnowflakeStoredProcedureTaskSourceAdapter.

        Sets up the configuration attribute and loads the configuration from configuration.
        Registers a cleanup handler to close connections gracefully on program exit.
        """
        super().__init__()
        try:
            self.connection_name = program_config[f"{config_keys.TASK_SOURCE}"].connection_name
        except (KeyError, AttributeError) as e:
            raise custom_exceptions.ConfigurationError(
                "Snowflake stored procedure task source configuration is missing or incomplete. "
                "Please ensure the 'connection_name' field is present in the "
                "'task_source' section of the configuration file."
            ) from e

        try:
            self.agent_id = program_config[f"{config_keys.APPLICATION__AGENT_ID}"]
        except (KeyError, AttributeError) as e:
            raise custom_exceptions.ConfigurationError("Agent ID is missing or incomplete.") from e

        self.snowflake_datasource: SnowflakeDataSource = SnowflakeDataSource(connection_name=self.connection_name)

    def get_tasks(self) -> list[dict]:
        """
        Retrieve tasks from the Task Source.

        Makes a GET request to fetch tasks from the Task Source.

        Returns:
            list[dict]: List of task dictionaries from the Task Source response

        Raises:
            Exception: If the Task Source request fails

        """
        pull_tasks_statement = (
            f"CALL {self.SCHEMA}.{self.PULL_TASKS_SP_NAME}("
            f"'{self.agent_id}', '{self.AGENT_TYPE}', {self.MAX_TASKS_PER_FETCH})"
        )  # TODO(SNOW-2910666): Sanitization for this
        with self.snowflake_datasource as snowflake_datasource:
            try:
                raw_results = snowflake_datasource.execute_statement(pull_tasks_statement)

                tasks_list = []
                for raw_task in raw_results:
                    raw_task_payload = json.loads(raw_task["PAYLOAD"])
                    task_obj = Task(
                        id=raw_task["ID"],
                        engine=raw_task_payload["source_type"],
                        database=raw_task_payload["database"],
                        schema=raw_task_payload["schema"],
                        statement=raw_task_payload["statement_location_id"],
                        source_type="jdbc",
                        upload_type=raw_task_payload["target_type"],
                        upload_path=raw_task_payload["target_id"],
                    )
                    tasks_list.append(task_obj.to_dict())
            except Exception as e:
                raise Exception(f"Failed to pull tasks executing statement: {pull_tasks_statement}.") from e

            return tasks_list

    def complete_task(self, task_id: str) -> None:
        """
        Mark a task as completed.

        Args:
            task_id: The identifier of the task to mark as completed

        """
        complete_task_statement = f"CALL {self.SCHEMA}.{self.COMPLETE_TASK_SP_NAME}(" f"'{self.agent_id}', {task_id})"
        with self.snowflake_datasource as snowflake_datasource:
            try:
                raw_result = next(iter(snowflake_datasource.execute_statement(complete_task_statement)), None)
            except Exception as e:
                raise Exception(
                    f"Failed to mark task '{task_id}' as completed executing statement: {complete_task_statement}."
                ) from e
            if raw_result is None or not raw_result.get(self.COMPLETED_TASK_STATUS_KEY, None):
                raise Exception(
                    f"Failed to mark task '{task_id}' as completed executing statement: {complete_task_statement}."
                )

    def fail_task(self, task_id: str, error_message: str | None = None) -> None:
        """
        Mark a task as failed.

        Args:
            task_id: The identifier of the task to mark as failed
            error_message: Optional error message describing the failure

        """
        with self.snowflake_datasource as snowflake_datasource:
            if error_message is None:
                fail_task_statement = (
                    f"CALL {self.SCHEMA}.{self.FAIL_TASK_SP_NAME}("
                    f"{task_id}, '{self.agent_id}', 'No error message provided.')"
                )  # TODO(SNOW-2910666): Sanitization
            else:
                error_message = error_message.replace("'", "''")
                fail_task_statement = (
                    f"CALL {self.SCHEMA}.{self.FAIL_TASK_SP_NAME}(" f"{task_id}, '{self.agent_id}', '{error_message}')"
                )  # TODO(SNOW-2910666): Sanitization
            try:
                raw_result = next(iter(snowflake_datasource.execute_statement(fail_task_statement)), None)
            except Exception as e:
                raise Exception(
                    f"Failed to mark task '{task_id}' as failed executing statement: {fail_task_statement}."
                ) from e

            if raw_result is None or not raw_result.get(self.FAILED_TASK_STATUS_KEY, None):
                raise Exception(
                    f"Failed to mark task '{task_id}' as failed executing statement: {fail_task_statement}."
                )
