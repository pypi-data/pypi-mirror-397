"""Task source configuration module."""

from data_exchange_agent.config.sections.task_sources.api import ApiConfig
from data_exchange_agent.config.sections.task_sources.snowflake_stored_procedure import SnowflakeStoredProcedureConfig
from data_exchange_agent.config.sections.task_sources.task_source import TaskSourceConfig
from data_exchange_agent.config.sections.task_sources.task_source_registry import TaskSourceRegistry
from data_exchange_agent.constants.task_source_types import TaskSourceType


# Register task source types
TaskSourceRegistry.register(TaskSourceType.API, ApiConfig)
TaskSourceRegistry.register(TaskSourceType.SNOWFLAKE_STORED_PROCEDURE, SnowflakeStoredProcedureConfig)

__all__ = ["ApiConfig", "SnowflakeStoredProcedureConfig", "TaskSourceConfig", "TaskSourceRegistry"]
