"""
Task Source components for the data exchange agent.

This package contains modules for handling Task Source requests, responses, and
management of the data exchange agent service.
"""

from data_exchange_agent.constants.task_source_types import TaskSourceType
from data_exchange_agent.task_sources.api import APITaskSourceAdapter
from data_exchange_agent.task_sources.snowflake_stored_procedure import SnowflakeStoredProcedureTaskSourceAdapter
from data_exchange_agent.task_sources.task_source_adapter_registry import TaskSourceAdapterRegistry


# Register all available task source adapters
TaskSourceAdapterRegistry.register(TaskSourceType.API, APITaskSourceAdapter)
TaskSourceAdapterRegistry.register(TaskSourceType.SNOWFLAKE_STORED_PROCEDURE, SnowflakeStoredProcedureTaskSourceAdapter)
# Future adapters can be registered here:
# TaskSourceAdapterRegistry.register(TaskSourceType.SF_TABLE, SFTableTaskSourceAdapter)
# TaskSourceAdapterRegistry.register(TaskSourceType.FILE, FileTaskSourceAdapter)

__all__ = ["APITaskSourceAdapter", "TaskSourceAdapterRegistry"]
