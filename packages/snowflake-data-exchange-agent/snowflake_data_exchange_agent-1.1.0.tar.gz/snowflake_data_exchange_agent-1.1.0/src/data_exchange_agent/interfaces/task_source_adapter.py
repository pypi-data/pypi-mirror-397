"""
Task Source Adapter interface for data exchange agent.

This module defines the abstract interface for managing task source interactions.
It provides a standard contract that all Task Source Adapter implementations must follow.
"""

from abc import ABC, abstractmethod


class TaskSourceAdapter(ABC):
    """
    Interface for managing Task Source interactions.

    This abstract base class defines the interface that Task Source Adapter implementations
    must follow to provide Task Source communication functionality including configuration,
    task retrieval, and task updates.
    """

    @abstractmethod
    def get_tasks(self) -> list[dict]:
        """
        Retrieve tasks from the Task Source.

        Returns:
            list[dict]: List of task dictionaries from the Task Source response

        Raises:
            Exception: If the Task Source request fails

        """
        pass

    @abstractmethod
    def complete_task(self, task_id: str) -> None:
        """
        Mark a task as completed.

        Args:
            task_id: The identifier of the task to mark as completed

        """
        pass

    @abstractmethod
    def fail_task(self, task_id: str, error_message: str | None = None) -> None:
        """
        Mark a task as failed.

        Args:
            task_id: The identifier of the task to mark as failed
            error_message: Optional error message describing the failure

        """
        pass
