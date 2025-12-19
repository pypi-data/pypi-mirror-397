"""
API management module for handling external API interactions.

This module provides the APITaskSourceAdapter class for managing communication with
external APIs, including configuration, task retrieval, and task updates.
"""

import requests

from dependency_injector.wiring import Provide, inject

from data_exchange_agent import custom_exceptions
from data_exchange_agent.config import ConfigManager
from data_exchange_agent.constants import config_keys, container_keys
from data_exchange_agent.interfaces.task_source_adapter import TaskSourceAdapter


class APITaskSourceAdapter(TaskSourceAdapter):
    """
    Manages API interactions for the Data Exchange Agent.

    This class handles communication with the external API service, including:
    - Loading API configuration
    - Retrieving tasks from the API
    - Updating task status and details

    The API configuration is loaded from a TOML configuration file and used to configure the API.
    """

    BASE_URL = "http://127.0.0.1:5000"
    TIMEOUT_SECONDS = (10, 30)  # (connect timeout, read timeout)

    @inject
    def __init__(self, program_config: ConfigManager = Provide[container_keys.PROGRAM_CONFIG]) -> None:
        """
        Initialize the APITaskSourceAdapter.

        Sets up the configuration attribute and loads the configuration from configuration.
        """
        super().__init__()
        try:
            self.api_key = program_config[config_keys.TASK_SOURCE].key
        except (KeyError, AttributeError) as e:
            raise custom_exceptions.ConfigurationError(
                "API task source configuration is missing or incomplete. "
                "Please ensure the 'key' field is present in the 'task_source' section of the configuration file."
            ) from e

    def get_tasks(self) -> list[dict]:
        """
        Retrieve tasks from the Task Source.

        Makes a GET request to fetch tasks from the Task Source.

        Returns:
            list[dict]: List of task dictionaries from the Task Source response

        Raises:
            Exception: If the Task Source request fails

        """
        response = requests.get(
            f"{self.BASE_URL}/tasks?agent_id=1&group_id=1",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()["tasks"]

    def complete_task(self, task_id: str) -> None:
        """
        Mark a task as completed.

        Makes a PUT request to mark a task as completed in the Task Source.

        Args:
            task_id: The identifier of the task to mark as completed

        Raises:
            Exception: If the Task Source request fails

        """
        response = requests.put(
            f"{self.BASE_URL}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.TIMEOUT_SECONDS,
        )
        response.raise_for_status()

    def fail_task(self, task_id: str, error_message: str | None = None) -> None:
        """
        Mark a task as failed.

        Args:
            task_id: The identifier of the task to mark as failed
            error_message: Optional error message describing the failure

        Raises:
            Exception: If the Task Source request fails

        """
        response = requests.put(
            f"{self.BASE_URL}/tasks/{task_id}/fail",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.TIMEOUT_SECONDS,
            json={"error_message": error_message},
        )
        response.raise_for_status()
