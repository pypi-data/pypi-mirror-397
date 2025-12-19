"""
Interface definitions and abstract base classes.

This package contains abstract base classes and interfaces that define
contracts for data sources, task queues, and other components.
"""

from data_exchange_agent.interfaces.data_source import DataSourceInterface
from data_exchange_agent.interfaces.task_queue import TaskQueueInterface
from data_exchange_agent.interfaces.task_source_adapter import TaskSourceAdapter
from data_exchange_agent.interfaces.uploader import UploaderInterface


__all__ = ["DataSourceInterface", "TaskQueueInterface", "TaskSourceAdapter", "UploaderInterface"]
