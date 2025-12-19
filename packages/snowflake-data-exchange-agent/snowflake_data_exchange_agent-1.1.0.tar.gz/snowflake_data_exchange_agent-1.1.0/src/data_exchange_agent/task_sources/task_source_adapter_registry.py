"""Task source adapter registry for dynamic class registration."""

from data_exchange_agent.interfaces.task_source_adapter import TaskSourceAdapter
from data_exchange_agent.utils.base_registry import BaseRegistry


class TaskSourceAdapterRegistry(BaseRegistry[TaskSourceAdapter]):
    """Registry for task source adapter classes."""

    _registry_type_name = "task_source_adapter"
