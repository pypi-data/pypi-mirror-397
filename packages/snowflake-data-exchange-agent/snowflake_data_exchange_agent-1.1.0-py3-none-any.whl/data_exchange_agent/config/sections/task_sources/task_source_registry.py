"""Task source registry for dynamic class registration."""

from data_exchange_agent.config.sections.task_sources.task_source import TaskSourceConfig
from data_exchange_agent.utils.base_registry import BaseRegistry


class TaskSourceRegistry(BaseRegistry[TaskSourceConfig]):
    """Registry for task source configuration classes."""

    _registry_type_name = "task source"
